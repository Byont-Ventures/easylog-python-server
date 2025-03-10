# Python standard library imports
import base64
import io
import json
import re
import time
from collections.abc import AsyncGenerator
from typing import TypedDict

import httpx

# Third-party imports
from dotenv import load_dotenv
from PIL import Image
from pydantic import BaseModel, Field

from src.agents.anthropic_agent import AnthropicAgent
from src.agents.tools.planning_tools import PlanningTools
from src.logger import logger
from src.models.messages import Message, MessageContent
from src.utils.function_to_anthropic_tool import function_to_anthropic_tool

# Laad alle variabelen uit .env
load_dotenv()


class EasylogData(TypedDict):
    """
    Defines the structure for Easylog data
    """

    status: str
    datum: str
    object: str
    statusobject: str


# Configuration class for AnthropicEasylog agent
class AnthropicEasylogAgentConfig(BaseModel):
    max_report_entries: int = Field(
        default=100,
        description="Maximum number of entries to fetch from the database for reports",
    )
    debug_mode: bool = Field(default=True, description="Enable debug mode with additional logging")
    image_max_width: int = Field(default=1200, description="Maximum width for processed images in pixels")
    image_quality: int = Field(default=90, description="JPEG quality for processed images (1-100)")


# Agent class that integrates with Anthropic's Claude API for EasyLog data analysis
class AnthropicEasylogAgent(AnthropicAgent[AnthropicEasylogAgentConfig]):
    def __init__(self, *args, **kwargs) -> None:
        # Call the parent class init
        super().__init__(*args, **kwargs)

        # Setup planning tools
        self._planning_tools = PlanningTools(self.easylog_backend)

        # Extra logging om tools bij te houden
        self.available_tools = []
        self.logger.info("EasylogAgent initialized with planning tools")

        # Disable debug mode to avoid loading debug tools
        self.config.debug_mode = False

    def _describe_available_tools(self):
        """Log beschikbare tools in de class en filter debug tools uit"""
        all_tools = [
            "tool_store_memory",
            "tool_get_easylog_data",
            "tool_generate_monthly_report",
            "tool_get_object_history",
            "tool_download_image_from_url",
            "tool_search_pdf",
            "tool_clear_memories",
            # Planning tools
            "tool_get_planning_projects",
            "tool_get_planning_project",
            "tool_update_planning_project",
            "tool_get_planning_phases",
            "tool_get_planning_phase",
            "tool_update_planning_phase",
            "tool_create_planning_phase",
            "tool_get_resources",
            "tool_get_projects_of_resource",
            "tool_create_multiple_allocations",
            "tool_get_resource_groups",
        ]

        self.available_tools = all_tools
        self.logger.info(f"Beschikbare tools voor EasylogAgent: {', '.join(all_tools)}")

    def _extract_user_info(self, message_text: str) -> list[str]:
        """
        Detecteert automatisch belangrijke informatie in het bericht van de gebruiker

        Args:
            message_text: De tekstinhoud van het bericht van de gebruiker

        Returns:
            Een lijst met gedetecteerde informatie
        """
        detected_info = []

        # Namen detecteren
        name_patterns = [
            r"(?i)(?:ik ben|mijn naam is|ik heet|noem mij)\s+([A-Za-z\s]+)",
            r"(?i)naam(?:\s+is)?\s+([A-Za-z\s]+)",
        ]

        for pattern in name_patterns:
            matches = re.findall(pattern, message_text)
            for match in matches:
                name = match.strip()
                if name and len(name) > 1:  # Minimale lengte om valse positieven te vermijden
                    detected_info.append(f"Naam: {name}")
                    self.logger.info(f"Detected user name: {name}")

        # Functietitels detecteren
        role_patterns = [
            r"(?i)(?:ik ben|ik werk als)(?:\s+de|een|)?\s+([A-Za-z\s]+manager|[A-Za-z\s]+directeur|[A-Za-z\s]+analist|[A-Za-z\s]+medewerker|[A-Za-z\s]+monteur)",
            r"(?i)functie(?:\s+is)?\s+([A-Za-z\s]+)",
        ]

        for pattern in role_patterns:
            matches = re.findall(pattern, message_text)
            for match in matches:
                role = match.strip()
                if role and len(role) > 3:  # Minimale lengte om valse positieven te vermijden
                    detected_info.append(f"Functie: {role}")
                    self.logger.info(f"Detected user role: {role}")

        # Afdelingen detecteren
        department_patterns = [
            r"(?i)(?:ik werk bij|ik zit bij)(?:\s+de)?\s+afdeling\s+([A-Za-z\s]+)",
            r"(?i)afdeling(?:\s+is)?\s+([A-Za-z\s]+)",
        ]

        for pattern in department_patterns:
            matches = re.findall(pattern, message_text)
            for match in matches:
                department = match.strip()
                if department and len(department) > 2:  # Minimale lengte om valse positieven te vermijden
                    detected_info.append(f"Afdeling: {department}")
                    self.logger.info(f"Detected user department: {department}")

        # Rapportagevoorkeuren detecteren
        report_patterns = [
            r"(?i)(?:ik wil|graag|liefst)(?:\s+\w+)?\s+(dagelijks|wekelijks|maandelijks|kwartaal|jaarlijks)e?\s+rapport",
            r"(?i)rapport(?:en|ages)?(?:\s+graag)?\s+(dagelijks|wekelijks|maandelijks|kwartaal|jaarlijks)",
        ]

        for pattern in report_patterns:
            matches = re.findall(pattern, message_text)
            for match in matches:
                frequency = match.strip().lower()
                detected_info.append(f"Voorkeur: {frequency}e rapportages")
                self.logger.info(f"Detected reporting preference: {frequency}")

        return detected_info

    async def _store_detected_name(self, message_text: str):
        """
        Detecteert en slaat belangrijke informatie op uit het bericht van de gebruiker

        Args:
            message_text: De tekstinhoud van het bericht van de gebruiker
        """
        detected_info = self._extract_user_info(message_text)

        if not detected_info:
            return

        # Direct store_memory aanroepen voor elke gedetecteerde informatie
        for info in detected_info:
            await self._store_memory_internal(info)

    async def _store_memory_internal(self, memory: str):
        """
        Interne functie om herinneringen op te slaan met controle op duplicaten

        Args:
            memory: De herinnering die moet worden opgeslagen
        """
        memory = memory.strip()
        if not memory:
            return

        # Haal huidige herinneringen op
        current_memories = self.get_metadata("memories", default=[])

        # Extract type (alles voor de eerste ":")
        memory_type = memory.split(":", 1)[0].strip().lower() if ":" in memory else ""

        # Zoek naar bestaande herinnering van hetzelfde type
        existing_index = -1
        for i, existing_memory in enumerate(current_memories):
            existing_type = existing_memory.split(":", 1)[0].strip().lower() if ":" in existing_memory else ""
            if memory_type and existing_type == memory_type:
                existing_index = i
                break

        # Update bestaande of voeg nieuwe toe
        if existing_index >= 0:
            # Vervang bestaande herinnering
            current_memories[existing_index] = memory
            self.logger.info(f"Updated existing memory: {memory}")
        else:
            # Voeg nieuwe herinnering toe
            current_memories.append(memory)
            self.logger.info(f"Added new memory: {memory}")

        # Sla bijgewerkte herinneringen op
        self.set_metadata("memories", current_memories)

    async def on_message(self, messages: list[Message]) -> AsyncGenerator[MessageContent, None]:
        """
        Deze functie handelt elk bericht van de gebruiker af.
        """
        # Verwijder eventuele debug tools die in de code zijn overgebleven
        self.logger.info("Removing any debug tools that might still be in code")
        # Debug mode debug tools verwijderen
        self.config.debug_mode = False

        # Beschrijf beschikbare tools
        self._describe_available_tools()

        # Log the incoming message for debugging
        if messages and len(messages) > 0:
            last_message = messages[-1]
            if last_message.role == "user" and isinstance(last_message.content, str):
                self.logger.info(f"Processing user message: {last_message.content[:100]}...")
                # Automatisch naam detecteren en opslaan
                await self._store_detected_name(last_message.content)

        # Convert messages to a format Claude understands
        message_history = self._convert_messages_to_anthropic_format(messages)

        if self.config.debug_mode:
            self.logger.debug(f"Converted message history: {message_history}")

        # Memories ophalen
        memories = self.get_metadata("memories", default=[])
        logger.info(f"Current memories: {memories}")

        def tool_clear_memories():
            """
            Wis alle opgeslagen herinneringen en de gespreksgeschiedenis.
            """
            self.set_metadata("memories", [])
            message_history.clear()
            self.logger.info("Memories and conversation history cleared")
            return "Alle herinneringen en de gespreksgeschiedenis zijn gewist."

        async def tool_store_memory(memory: str) -> str:
            """
            Store a memory in the database.
            """
            current_memory = self.get_metadata("memories", default=[])
            current_memory.append(memory)
            self.logger.info(f"Storing memory: {memory}")
            self.set_metadata("memories", current_memory)
            return "Memory stored"

        async def tool_get_easylog_data():
            """
            Haalt de controles op uit EasyLog en maakt ze leesbaar.
            """
            try:
                self.logger.info("Fetching EasyLog data")
                with self.easylog_db.cursor() as cursor:
                    query = """
                        SELECT 
                            JSON_UNQUOTE(JSON_EXTRACT(data, '$.datum')) as datum,
                            JSON_UNQUOTE(JSON_EXTRACT(data, '$.object')) as object,
                            JSON_UNQUOTE(JSON_EXTRACT(data, '$.controle[0].statusobject')) as statusobject
                        FROM follow_up_entries
                        ORDER BY created_at DESC
                        LIMIT 100
                    """
                    self.logger.debug(f"Executing query: {query}")
                    cursor.execute(query)
                    entries = cursor.fetchall()
                    self.logger.debug(f"Query returned {len(entries)} entries")

                    if not entries:
                        return "Geen controles gevonden"

                    results = ["🔍 Laatste controles:"]
                    for entry in entries:
                        datum, object_value, statusobject = entry
                        # Pas de statusobject waarde aan
                        if statusobject == "Ja":
                            statusobject = "Akkoord"
                        elif statusobject == "Nee":
                            statusobject = "Niet akkoord"

                        results.append(f"Datum: {datum}, Object: {object_value}, Status object: {statusobject}")
                    return "\n".join(results)

            except Exception as e:
                logger.error(f"Fout bij ophalen follow-up entries: {str(e)}")
                return f"Er is een fout opgetreden: {str(e)}"

        async def tool_generate_monthly_report(month: int, year: int):
            """
            Genereert een maandrapport voor de opgegeven maand en jaar.
            """
            try:
                self.logger.info(f"Generating monthly report for {month}/{year}")
                with self.easylog_db.cursor() as cursor:
                    query = """
                        SELECT 
                            JSON_UNQUOTE(JSON_EXTRACT(data, '$.datum')) as datum,
                            JSON_UNQUOTE(JSON_EXTRACT(data, '$.object')) as object,
                            JSON_UNQUOTE(JSON_EXTRACT(data, '$.controle[0].statusobject')) as statusobject,
                            created_at
                        FROM follow_up_entries
                        WHERE MONTH(created_at) = %s AND YEAR(created_at) = %s
                        ORDER BY created_at DESC
                    """
                    self.logger.debug(f"Executing query with params: {month}, {year}")
                    cursor.execute(query, (month, year))
                    entries = cursor.fetchall()
                    self.logger.debug(f"Query returned {len(entries)} entries")

                    if not entries:
                        return f"Geen controles gevonden voor {month}-{year}"

                    # Telling van statusobjecten
                    status_counts = {"Akkoord": 0, "Niet akkoord": 0, "Anders": 0}
                    objects = set()

                    for entry in entries:
                        datum, object_value, statusobject, created_at = entry

                        # Object toevoegen aan set voor unieke telling
                        if object_value:
                            objects.add(object_value)

                        # Status tellen
                        if statusobject == "Ja":
                            status_counts["Akkoord"] += 1
                        elif statusobject == "Nee":
                            status_counts["Niet akkoord"] += 1
                        else:
                            status_counts["Anders"] += 1

                    # Maandnamen in Nederlands
                    month_names = {
                        1: "januari",
                        2: "februari",
                        3: "maart",
                        4: "april",
                        5: "mei",
                        6: "juni",
                        7: "juli",
                        8: "augustus",
                        9: "september",
                        10: "oktober",
                        11: "november",
                        12: "december",
                    }

                    month_name = month_names.get(month, str(month))

                    # Rapportopbouw
                    report = [
                        f"📊 **Maandrapport {month_name} {year}**",
                        "",
                        "**Samenvatting:**",
                        f"- Totaal aantal controles: {len(entries)}",
                        f"- Unieke objecten gecontroleerd: {len(objects)}",
                        "- Status verdeling:",
                        f"  - Akkoord: {status_counts['Akkoord']} ({round(status_counts['Akkoord'] / len(entries) * 100)}%)",
                        f"  - Niet akkoord: {status_counts['Niet akkoord']} ({round(status_counts['Niet akkoord'] / len(entries) * 100)}%)",
                        f"  - Anders: {status_counts['Anders']} ({round(status_counts['Anders'] / len(entries) * 100)}%)",
                    ]

                    return "\n".join(report)

            except Exception as e:
                logger.error(f"Fout bij genereren maandrapport: {str(e)}")
                return f"Er is een fout opgetreden bij het genereren van het rapport: {str(e)}"

        async def tool_get_object_history(object_name: str, limit: int = 10):
            """
            Haalt de geschiedenis op van een specifiek object.
            """
            try:
                self.logger.info(f"Fetching history for object: {object_name}, limit: {limit}")
                with self.easylog_db.cursor() as cursor:
                    query = """
                        SELECT 
                            JSON_UNQUOTE(JSON_EXTRACT(data, '$.datum')) as datum,
                            JSON_UNQUOTE(JSON_EXTRACT(data, '$.controle[0].statusobject')) as statusobject,
                            created_at
                        FROM follow_up_entries
                        WHERE JSON_UNQUOTE(JSON_EXTRACT(data, '$.object')) = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                    """
                    self.logger.debug(f"Executing query with params: {object_name}, {limit}")
                    cursor.execute(query, (object_name, limit))
                    entries = cursor.fetchall()
                    self.logger.debug(f"Query returned {len(entries)} entries")

                    if not entries:
                        return f"Geen geschiedenis gevonden voor object: {object_name}"

                    results = [f"📜 **Geschiedenis voor {object_name}:**"]

                    for entry in entries:
                        datum, statusobject, created_at = entry

                        if statusobject == "Ja":
                            statusobject = "Akkoord"
                        elif statusobject == "Nee":
                            statusobject = "Niet akkoord"

                        results.append(f"Datum: {datum}, Status: {statusobject}")

                    return "\n".join(results)

            except Exception as e:
                logger.error(f"Fout bij ophalen object geschiedenis: {str(e)}")
                return f"Er is een fout opgetreden: {str(e)}"

        def tool_download_image_from_url(url: str) -> str:
            """
            Download een afbeelding van een URL en geef deze terug als base64-gecodeerde data-URL.
            De afbeelding kan dan direct in HTML/markdown weergegeven worden.
            """
            try:
                # Verbeterde logging met meer focus op grootte metrics
                self.logger.info("[IMAGE] ===== START AFBEELDING VERWERKING =====")
                self.logger.info(f"[IMAGE] URL: {url}")
                self.logger.info(
                    f"[IMAGE] Configuratie: max_width={self.config.image_max_width}px, quality={self.config.image_quality}%"
                )

                # Timeout toevoegen om hangende requests te voorkomen
                response = httpx.get(url, timeout=15.0)
                content_length = len(response.content)
                self.logger.info(f"[IMAGE] Ontvangen afbeeldingsgrootte: {content_length / 1024 / 1024:.2f} MB")

                # Check of de response OK is
                if response.status_code != 200:
                    self.logger.error(f"[IMAGE] Fout bij downloaden afbeelding: {response.status_code}")
                    return "Fout: kon afbeelding niet downloaden"

                # Kleinere limiet voor trage verbindingen
                MAX_COMPRESSED_SIZE = 200 * 1024  # Van 250KB naar 200KB voor betere streaming

                # Hard streaming limit voor verbindingsproblemen
                MAX_STREAMING_SIZE = 400 * 1024  # Maximaal 400KB voor streaming

                # Directe fallback voor zeer grote afbeeldingen bij trage verbindingen
                FORCE_THUMBNAIL_SIZE = 2 * 1024 * 1024  # 2MB force thumbnail

                # Voor zeer grote afbeeldingen tonen we een waarschuwing
                is_very_large_image = False
                is_extremely_large_image = False
                needs_streaming_optimization = False

                # Verklein de afbeelding voor betere performance en streaming
                try:
                    # Laad de afbeelding
                    img = Image.open(io.BytesIO(response.content))

                    # Originele afmetingen en grootte
                    original_width, original_height = img.size
                    original_size = len(response.content)
                    self.logger.info(f"[IMAGE] Originele afmetingen: {original_width}x{original_height}")
                    self.logger.info(f"[IMAGE] Originele bestandsgrootte: {original_size / 1024 / 1024:.2f} MB")

                    # Streaming optimalisatie voor grote afbeeldingen (vanaf 5MB)
                    if original_size > 5 * 1024 * 1024:
                        needs_streaming_optimization = True
                        self.logger.warning(
                            f"[IMAGE] Streaming optimalisatie geactiveerd voor {original_size / 1024 / 1024:.2f} MB afbeelding"
                        )

                    # Voor extreem grote afbeeldingen, DIRECTE thumbnail zonder verdere verwerking
                    if original_size > 8 * 1024 * 1024:  # Verlaagd van 10MB naar 8MB voor betere ondersteuning
                        self.logger.warning(
                            f"[IMAGE] EXTREEM grote afbeelding gedetecteerd: {original_size / 1024 / 1024:.2f} MB - DIRECTE THUMBNAIL"
                        )

                        # KRITISCH: Minimale verwerking voor zeer grote bestanden
                        # Maak een kleine thumbnail zonder enige tussenstappen
                        try:
                            # Gebruik een extreme verkleining voor grote afbeeldingen
                            thumb_img = img.copy()
                            # Forceer een zeer kleine thumbnail breedte
                            thumb_width = 300
                            thumb_img.thumbnail(
                                (thumb_width, int(thumb_width * thumb_img.height / thumb_img.width)),
                                Image.Resampling.NEAREST,
                            )  # Gebruik NEAREST voor snelheid

                            # Sla op met zeer lage kwaliteit voor snelle weergave
                            with io.BytesIO() as thumb_buffer:
                                # Gebruik lage kwaliteit en snellere compressie
                                thumb_img.save(thumb_buffer, format="JPEG", quality=50, optimize=False)
                                thumb_buffer.seek(0)
                                thumb_data = thumb_buffer.getvalue()

                            # Extra kleine thumbnail, max ~50KB
                            thumb_data_b64 = base64.b64encode(thumb_data).decode("utf-8")
                            thumb_url = f"data:image/jpeg;base64,{thumb_data_b64}"

                            # Log en return onmiddellijk
                            self.logger.warning(
                                f"[IMAGE] EXTREEM GROTE AFBEELDING: Directe thumbnail verstuurd ({len(thumb_data) / 1024:.1f}KB)"
                            )
                            self.logger.info(
                                "[IMAGE] ===== EINDE AFBEELDING VERWERKING (GROTE AFBEELDING DIRECTE THUMBNAIL) ====="
                            )

                            # Stuur direct de thumbnail terug zonder opties
                            return f"data:image/jpeg;base64,{thumb_data_b64}\n\n**Zeer grote afbeelding ({original_size / 1024 / 1024:.1f} MB) - Dit is een voorvertoning. De volledige versie is beschikbaar na vernieuwen van de chat.**"

                        except Exception as thumb_error:
                            # Als zelfs de thumbnail faalt, log en ga door naar fallback
                            self.logger.error(f"[IMAGE] Thumbnail fout: {str(thumb_error)}")
                            pass

                        # Als we hier komen, dan is zelfs de thumbnail mislukt
                        # Ga door naar de normale code, maar met zeer agressieve verkleining
                        is_extremely_large_image = True
                        is_very_large_image = True
                        target_width = 500  # Kleinere breedte
                        quality = 60  # Lagere kwaliteit
                    elif original_size > 5 * 1024 * 1024:  # > 5MB maar < 8MB
                        is_very_large_image = True
                        self.logger.info(
                            f"[IMAGE] Zeer grote afbeelding gedetecteerd: {original_size / 1024 / 1024:.2f} MB"
                        )
                        target_width = 650  # Kleinere breedte om grootte te beperken
                        quality = 75  # Lagere kwaliteit
                    elif original_size > 3 * 1024 * 1024:  # >3MB
                        target_width = 800  # Van 900px naar 800px voor betere compressie
                        quality = 80  # Van 85% naar 80%
                    else:
                        # Gebruik configuratie voor normale afbeeldingen maar met iets lagere kwaliteit
                        target_width = min(self.config.image_max_width, 1000)  # Niet groter dan 1000px
                        quality = min(
                            80, self.config.image_quality
                        )  # Kwaliteit begrenzen op 80% voor betere compressie

                    self.logger.info(f"[IMAGE] Target instellingen: {target_width}px breed, {quality}% kwaliteit")

                    # Streaming optimalisatie: maak direct thumbnail voor grote afbeeldingen
                    if needs_streaming_optimization and original_size > FORCE_THUMBNAIL_SIZE:
                        self.logger.warning(
                            f"[IMAGE] Direct thumbnail genereren voor grote afbeelding ({original_size / (1024 * 1024):.2f} MB)"
                        )
                        # Maak een kleine thumbnail voor directe weergave
                        thumb_width = 300  # Kleine thumbnail
                        thumb_quality = 50  # Lagere kwaliteit voor snelle weergave

                        # Creëer thumbnail voor snelle weergave met NEAREST resampling (sneller)
                        thumbnail_img = img.copy()
                        thumbnail_img.thumbnail(
                            (thumb_width, int(thumb_width * img.height / img.width)), Image.Resampling.NEAREST
                        )

                        with io.BytesIO() as buffer:
                            thumbnail_img.save(buffer, format="JPEG", quality=thumb_quality, optimize=False)
                            buffer.seek(0)
                            thumbnail_data = buffer.getvalue()

                        thumbnail_size = len(thumbnail_data)
                        thumbnail_data_b64 = base64.b64encode(thumbnail_data).decode("utf-8")

                        self.logger.info(
                            f"[IMAGE] Thumbnail gemaakt: {thumb_width}px breed, {thumb_quality}% kwaliteit, {thumbnail_size / 1024:.2f} KB"
                        )

                        # Stuur alleen de thumbnail met een melding dat het een grote afbeelding is
                        return f"data:image/jpeg;base64,{thumbnail_data_b64}\n\n**Grote afbeelding ({original_size / (1024 * 1024):.1f} MB) - Dit is een voorvertoning. De volledige versie is beschikbaar na vernieuwen van de chat.**"

                    # Bereken schaalfactor en nieuwe afmetingen
                    if original_width > target_width:
                        scale_factor = target_width / original_width
                        new_width = target_width
                        new_height = int(original_height * scale_factor)

                        # Verklein afbeelding - gebruik LANCZOS voor betere kwaliteit
                        img.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)
                        self.logger.info(f"[IMAGE] Verkleind naar: {img.width}x{img.height}")
                    else:
                        self.logger.info("[IMAGE] Afbeelding is kleiner dan max breedte, geen resize nodig")

                    # Converteer naar RGB indien nodig (voor PNG met transparantie)
                    if img.mode in ("RGBA", "LA"):
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3] if len(img.split()) > 3 else None)
                        img = background
                        self.logger.info("[IMAGE] Transparantie omgezet naar RGB")

                    # Bij extreem grote afbeeldingen direct naar de veilige kleine versie
                    if is_extremely_large_image:
                        self.logger.warning("[IMAGE] Direct naar veilige kleine versie voor extreem grote afbeelding")
                        img = img.resize((450, int(450 * img.height / img.width)), Image.Resampling.LANCZOS)
                        quality = 60  # Nog lagere kwaliteit voor extreem grote afbeeldingen

                    # Sla op in buffer met optimize=True voor betere compressie
                    with io.BytesIO() as buffer:  # Gebruik context manager voor automatische cleanup
                        img.save(buffer, format="JPEG", quality=quality, optimize=True)
                        buffer.seek(0)
                        image_data = buffer.getvalue()
                    image_size = len(image_data)
                    self.logger.info(
                        f"[IMAGE] Eerste compressie: {image_size / 1024:.2f} KB (doel: <{MAX_COMPRESSED_SIZE / 1024:.2f} KB)"
                    )

                    # Extra snelle check voor streaming problemen
                    if needs_streaming_optimization and image_size > MAX_STREAMING_SIZE:
                        self.logger.warning(
                            f"[IMAGE] Te groot voor streaming: {image_size / 1024:.2f} KB > {MAX_STREAMING_SIZE / 1024:.2f} KB"
                        )

                        # Maak een kleinere versie voor betere streaming
                        img = img.resize((400, int(400 * img.height / img.width)), Image.Resampling.LANCZOS)
                        with io.BytesIO() as buffer:
                            img.save(buffer, format="JPEG", quality=60, optimize=True)
                            buffer.seek(0)
                            image_data = buffer.getvalue()
                        image_size = len(image_data)
                        self.logger.info(f"[IMAGE] Streaming optimalisatie: {image_size / 1024:.2f} KB")

                    # Extra snelle check voor grote afbeeldingen die onmiddellijk verkleind moeten worden
                    if image_size > 2 * MAX_COMPRESSED_SIZE:
                        self.logger.warning(
                            f"[IMAGE] Afbeelding nog steeds te groot: {image_size / 1024:.2f} KB, directe verkleining"
                        )
                        # Drastischere verkleining
                        img = img.resize((400, int(400 * img.height / img.width)), Image.Resampling.LANCZOS)
                        with io.BytesIO() as buffer:
                            img.save(buffer, format="JPEG", quality=65, optimize=True)
                            buffer.seek(0)
                            image_data = buffer.getvalue()
                        image_size = len(image_data)
                        self.logger.info(f"[IMAGE] Na directe verkleining: {image_size / 1024:.2f} KB")

                    # Iteratieve compressie algoritme verbeteren
                    attempt = 1
                    max_attempts = 4  # Van 5 naar 4 pogingen voor snellere afhandeling

                    # Begin met meer agressieve verkleining voor grote afbeeldingen
                    quality_step = 15 if is_very_large_image else 10
                    min_quality = 45  # Lagere minimum kwaliteit toestaan voor zeer grote afbeeldingen

                    while image_size > MAX_COMPRESSED_SIZE and attempt <= max_attempts:
                        self.logger.info(
                            f"[IMAGE] Compressie iteratie {attempt}: {image_size / 1024:.2f} KB > {MAX_COMPRESSED_SIZE / 1024:.2f} KB"
                        )

                        attempt += 1

                        # Agressievere verkleining voor latere iteraties
                        resize_factor = 0.65 if attempt > 2 else 0.75  # Meer agressief verkleinen
                        new_width = int(img.width * resize_factor)
                        new_height = int(img.height * resize_factor)

                        # Grotere kwaliteitsreductie voor latere pogingen
                        new_quality = max(min_quality, quality - quality_step)
                        quality = new_quality

                        self.logger.info(f"[IMAGE] Iteratie {attempt}: {new_width}x{new_height}, kwaliteit {quality}%")

                        # Verklein afbeelding
                        img.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)

                        # Opnieuw opslaan met nieuwe instellingen
                        with io.BytesIO() as buffer:  # Hergebruik buffer in lus
                            img.save(buffer, format="JPEG", quality=quality, optimize=True)
                            buffer.seek(0)
                            image_data = buffer.getvalue()
                        image_size = len(image_data)

                        self.logger.info(f"[IMAGE] Na iteratie {attempt}: {image_size / 1024:.2f} KB")

                        # Aanpassing van compressiestappen voor volgende iteratie
                        quality_step = 8 if attempt > 2 else quality_step

                    # ALTIJD VEILIGE FALLBACK - ook als beeldgrootte nog te groot is na alle pogingen
                    # Base64 encoderen en resultaatgrootte loggen
                    image_data_b64 = base64.b64encode(image_data).decode("utf-8")
                    base64_size = len(image_data_b64)

                    # Logging van eindresultaat
                    self.logger.info(
                        f"[IMAGE] Compressie resultaat: {image_size / 1024:.2f} KB JPG → {base64_size / 1024:.2f} KB base64"
                    )
                    compression_ratio = (original_size - image_size) / original_size * 100
                    self.logger.info(f"[IMAGE] Compressie ratio: {compression_ratio:.2f}% verkleind")
                    self.logger.info(
                        f"[IMAGE] Uiteindelijke afmetingen: {img.width}x{img.height}, kwaliteit: {quality}%"
                    )

                    # BESLUIT LOGGING - belangrijk voor debugging
                    self.logger.warning(
                        f"[IMAGE] BESLUIT CHECK: size={image_size / 1024:.2f}KB, base64={base64_size / 1024:.2f}KB, max={MAX_COMPRESSED_SIZE / 1024:.2f}KB, attempts={attempt}"
                    )

                    # Speciale streaming controle voor grote afbeeldingen
                    if needs_streaming_optimization and base64_size > 500 * 1024:
                        self.logger.warning(
                            f"[IMAGE] Streaming limiet overschreden: {base64_size / 1024:.2f}KB > 500KB, extra compressie nodig"
                        )
                        # Extra agressieve verkleining voor streaming
                        img = img.resize((320, int(320 * img.height / img.width)), Image.Resampling.LANCZOS)
                        with io.BytesIO() as buffer:
                            img.save(buffer, format="JPEG", quality=55, optimize=True)
                            buffer.seek(0)
                            image_data = buffer.getvalue()
                        image_size = len(image_data)
                        image_data_b64 = base64.b64encode(image_data).decode("utf-8")
                        base64_size = len(image_data_b64)
                        self.logger.info(
                            f"[IMAGE] Na streaming optimalisatie: {image_size / 1024:.2f}KB, base64: {base64_size / 1024:.2f}KB"
                        )

                    # Implementeer een fallback mechanisme voor problematische beelden die nog steeds te groot zijn
                    if image_size > MAX_COMPRESSED_SIZE or base64_size > 600 * 1024:  # Verlaagd naar 600KB voor base64
                        # Als we na alle pogingen nog steeds te groot zijn, lever een vereenvoudigde versie
                        self.logger.warning(
                            f"[IMAGE] Fallback nodig: {image_size / 1024:.2f} KB > {MAX_COMPRESSED_SIZE / 1024:.2f} KB of base64 {base64_size / 1024:.2f} KB > 600 KB"
                        )

                        # Maak een GEGARANDEERD kleine versie
                        img = img.resize((320, int(320 * img.height / img.width)), Image.Resampling.LANCZOS)
                        with io.BytesIO() as buffer:
                            img.save(buffer, format="JPEG", quality=55, optimize=True)
                            buffer.seek(0)
                            image_data = buffer.getvalue()
                        image_size = len(image_data)
                        image_data_b64 = base64.b64encode(image_data).decode("utf-8")
                        base64_size = len(image_data_b64)

                        self.logger.info(
                            f"[IMAGE] FALLBACK: Verkleind naar 320px breed, 55% kwaliteit, {image_size / 1024:.2f} KB, base64: {base64_size / 1024:.2f} KB"
                        )

                        # Maak de data URL met de fallback versie
                        data_url = f"data:image/jpeg;base64,{image_data_b64}"

                        self.logger.info("[IMAGE] ===== EINDE AFBEELDING VERWERKING (FALLBACK) =====")
                        return f"{data_url}\n\n**Grote afbeelding ({original_size / 1024 / 1024:.2f} MB) - Dit is een verkleinde versie voor betere weergave.**"

                    # Check of base64 misschien te groot is voor chat interface
                    data_url = f"data:image/jpeg;base64,{image_data_b64}"

                    # Waarschuwing voor trage verbindingen zonder de afbeelding te vervangen
                    if needs_streaming_optimization:
                        self.logger.info("[IMAGE] ===== EINDE AFBEELDING VERWERKING (STREAMING GEOPTIMALISEERD) =====")
                        if not is_very_large_image:  # Alleen voor middelgrote afbeeldingen
                            return data_url

                    # Kritische waarschuwing als de base64 string nog steeds te groot is
                    if base64_size > 1024 * 1024:  # Meer dan 1MB base64 data
                        self.logger.warning(f"[IMAGE] Base64 output is zeer groot ({base64_size / 1024 / 1024:.2f} MB)")
                        self.logger.info("[IMAGE] ===== EINDE AFBEELDING VERWERKING (GROTE BASE64) =====")
                        return f"{data_url}\n\n**Grote afbeelding ({original_size / 1024 / 1024:.2f} MB) - De volledige versie is beschikbaar na vernieuwen van de chat.**"

                    if is_very_large_image:
                        self.logger.info("[IMAGE] ===== EINDE AFBEELDING VERWERKING (GROOT) =====")
                        return data_url

                    self.logger.info("[IMAGE] ===== EINDE AFBEELDING VERWERKING (SUCCES) =====")
                    return data_url

                except Exception as e:
                    self.logger.error(f"[IMAGE] Fout bij verkleinen afbeelding: {str(e)}")
                    import traceback

                    self.logger.error(f"[IMAGE] Details fout: {traceback.format_exc()}")

                    # Zelfs bij een fout proberen we een fallback te bieden
                    try:
                        if img:
                            # Creëer de meest eenvoudige versie mogelijk
                            img = img.resize((280, int(280 * img.height / img.width)), Image.Resampling.LANCZOS)
                            with io.BytesIO() as buffer:
                                img.save(buffer, format="JPEG", quality=50, optimize=True)
                                buffer.seek(0)
                                image_data = buffer.getvalue()
                            image_data_b64 = base64.b64encode(image_data).decode("utf-8")
                            data_url = f"data:image/jpeg;base64,{image_data_b64}"
                            return data_url
                    except:
                        pass

                    return f"Er is een fout opgetreden bij het verwerken van de afbeelding: {str(e)}"

            except Exception as e:
                self.logger.error(f"[IMAGE] Onverwachte fout: {str(e)}")
                import traceback

                self.logger.error(f"[IMAGE] Stacktrace: {traceback.format_exc()}")
                return f"Fout bij verwerken afbeelding: {str(e)}"

        async def tool_search_pdf(query: str) -> str:
            """
            Search for a PDF in the knowledge base.
            """
            knowledge_result = await self.search_knowledge(query)

            if (
                knowledge_result is None
                or knowledge_result.object is None
                or knowledge_result.object.name is None
                or knowledge_result.object.bucket_id is None
            ):
                return "Geen PDF gevonden"

            return json.dumps(
                {
                    "id": knowledge_result.id,
                    "markdown_content": knowledge_result.markdown_content,
                }
            )

        tools = [
            tool_store_memory,
            tool_get_easylog_data,
            tool_generate_monthly_report,
            tool_get_object_history,
            tool_download_image_from_url,
            tool_search_pdf,
            *self._planning_tools.all_tools,
            tool_clear_memories,
        ]

        # Print alle tools om te debuggen
        self.logger.info("All tools before filtering:")
        for tool in tools:
            self.logger.info(f" - {tool.__name__}")

        # Zet alle tools om naar het Anthropic formaat en filter debug tools
        anthropic_tools = []
        for tool in tools:
            # Expliciet alle tool-namen die we willen behouden
            if tool.__name__ in [
                "tool_store_memory",
                "tool_get_easylog_data",
                "tool_generate_monthly_report",
                "tool_get_object_history",
                "tool_download_image_from_url",
                "tool_search_pdf",
                "tool_clear_memories",
                # Planning tools namen
                "tool_get_planning_projects",
                "tool_get_planning_project",
                "tool_update_planning_project",
                "tool_get_planning_phases",
                "tool_get_planning_phase",
                "tool_update_planning_phase",
                "tool_create_planning_phase",
                "tool_get_resources",
                "tool_get_projects_of_resource",
                "tool_create_multiple_allocations",
                "tool_get_resource_groups",
            ]:
                anthropic_tools.append(function_to_anthropic_tool(tool))
            else:
                self.logger.warning(f"Skipping tool: {tool.__name__}")

        # Print alle tools na filtering om te debuggen
        self.logger.info("All tools after filtering:")
        for i, tool in enumerate(anthropic_tools):
            self.logger.info(f" - {i + 1}: {tool.function.name}")

        start_time = time.time()

        stream = await self.client.messages.create(
            # Gebruik Claude 3.7 Sonnet model
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            system=f"""Je bent een vriendelijke en behulpzame data-analist voor EasyLog.
Je taak is om gebruikers te helpen bij het analyseren van bedrijfsgegevens en het maken van overzichtelijke verslagen.

### BELANGRIJKE REGELS:
- Geef nauwkeurige en feitelijke samenvattingen van de EasyLog data!
- Help de gebruiker patronen te ontdekken in de controlegegevens
- Maak verslagen in tabellen end uidelijk en professioneel met goede opmaak
- Gebruik grafieken en tabellen waar mogelijk (markdown)
- Wees proactief in het suggereren van analyses die nuttig kunnen zijn

### Beschikbare tools:
- tool_get_easylog_data: Haalt de laatste controles op uit de EasyLog database
- tool_generate_monthly_report: Maakt een maandrapport met statistieken
- tool_get_object_history: Haalt de geschiedenis van een specifiek object op
- tool_store_memory: Slaat belangrijke informatie op voor later gebruik
- tool_clear_memories: Wist alle opgeslagen herinneringen
- tool_download_image_from_url: Download een afbeelding van een URL en geef deze terug als base64-gecodeerde data-URL
- tool_search_pdf: Zoek een PDF in de kennisbank

### Core memories
Core memories zijn belangrijke informatie die je moet onthouden over een gebruiker. Die verzamel je zelf met de tool "store_memory". Als de gebruiker bijvoorbeeld zijn naam vertelt, of een belangrijke gebeurtenis heeft meegemaakt, of een belangrijke informatie heeft geleverd, dan moet je die opslaan in de core memories.

Voorbeelden van belangrijke herinneringen om op te slaan:
- Naam van de gebruiker (bijv. "Naam: Jan")
- Functie (bijv. "Functie: Data Analist")
- Afdeling (bijv. "Afdeling: Financiën")
- Voorkeuren voor rapportages (bijv. "Voorkeur: wekelijkse rapportages")
- Specifieke behoeften voor data-analyse (bijv. "Behoefte: focus op niet-conforme objecten")

Je huidige core memories zijn:
{"\n- " + "\n- ".join(memories) if memories else " Geen memories opgeslagen"}

### Data analyse tips:
- Zoek naar trends over tijd
- Identificeer objecten met hoog risico (veel 'niet akkoord' statussen)
- Wijs op ongewone of afwijkende resultaten
- Geef context bij de cijfers waar mogelijk
- Vat grote datasets bondig samen
            """,
            messages=message_history,
            tools=anthropic_tools,
            stream=True,
        )

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Time taken for API call: {execution_time:.2f} seconds")

        if execution_time > 5.0:
            logger.warning(f"API call took longer than expected: {execution_time:.2f} seconds")

        async for content in self.handle_stream(
            stream,
            tools,
        ):
            if self.config.debug_mode:
                self.logger.debug(f"Streaming content: {str(content)[:100]}...")
            yield content
