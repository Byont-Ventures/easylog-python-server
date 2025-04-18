# Python standard library imports
import io
import json
import re
import time
from collections.abc import AsyncGenerator
from typing import TypedDict

# Third-party imports
from dotenv import load_dotenv
from PIL import Image
from pydantic import BaseModel, Field

from src.agents.anthropic_agent import AnthropicAgent
from src.logger import logger
from src.models.messages import Message, MessageContent
from src.models.charts import Chart
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
            "tool_search_pdf",
            "tool_load_image",
            "tool_clear_memories",
        ]

        self.available_tools = all_tools
        self.logger.info(f"Beschikbare tools voor EasylogAgent: {', '.join(all_tools)}")

    def _extract_user_info(self, message_text: str) -> list[str]:
        """
        Detecteert automatisch belangrijke informatie in het bericht van de gebruiker!!

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

    # --- Image Processing Helper Methods ---
    async def _attempt_load_image(self, _id: str, file_name: str) -> Image.Image | None:
        """Tries to load an image using various possible path variations."""
        possible_paths = [
            file_name,
            f"figures/{file_name}" if "/" not in file_name else file_name,
            file_name.replace("figures/", "") if file_name.startswith("figures/") else file_name,
            file_name.split("/")[-1],  # Only the filename
        ]

        last_error = None
        for path in possible_paths:
            try:
                # Use the base class method to load the image
                image_data = await super().load_image(_id, path)
                self.logger.info(f"[IMAGE] Successfully loaded with path: {path}")
                return image_data
            except Exception as e:
                last_error = e
                continue

        self.logger.warning(f"[IMAGE] Failed to load image {file_name} from {_id} with any path: {last_error}")
        return None

    def _convert_heic_to_jpeg(self, image_data: Image.Image) -> Image.Image:
        """Converts HEIC images to JPEG format."""
        if hasattr(image_data, 'format') and image_data.format == 'HEIC':
            try:
                with io.BytesIO() as buffer:
                    # Use a default quality for conversion
                    image_data.save(buffer, format="JPEG", quality=85)
                    buffer.seek(0)
                    converted_image = Image.open(buffer)
                    # Important: Copy the image data to avoid issues with closed buffer
                    image_data = converted_image.copy()
                    self.logger.info("[IMAGE] Converted HEIC to JPEG format")
            except Exception as e:
                self.logger.error(f"[IMAGE] Error converting HEIC: {str(e)}")
                # Return original if conversion fails
        return image_data

    def _apply_compression(self, image_data: Image.Image) -> tuple[Image.Image, float, float]:
        """Applies resizing and compression to the image."""
        original_size_kb = 0.0
        try:
            # Determine original size
            with io.BytesIO() as buffer:
                # Use the original format if available, fallback to PNG
                original_format = image_data.format if hasattr(image_data, 'format') and image_data.format else "PNG"
                # Ensure format is supported by PIL for saving, default to PNG
                if original_format.upper() not in ["PNG", "JPEG", "JPG", "GIF", "BMP", "TIFF"]:
                     original_format = "PNG"
                image_data.save(buffer, format=original_format)
                buffer.seek(0)
                original_size = len(buffer.getvalue())
            original_size_kb = original_size / 1024
            original_width, original_height = image_data.size

            # --- Compression Strategy ---
            target_kb = 50
            max_width = 800
            initial_quality = 60
            min_quality = 30

            # 1. Resize if dimensions exceed max_width
            resized_image = image_data
            if original_width > max_width:
                scale_factor = max_width / original_width
                new_height = int(original_height * scale_factor)
                self.logger.info(f"[IMAGE] Resizing from {original_width}x{original_height} to {max_width}x{new_height}")
                resized_image = image_data.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # 2. Convert to RGB if necessary (for JPEG saving)
            if resized_image.mode in ("RGBA", "LA", "P"): # Added 'P' for Palette mode
                 self.logger.info(f"[IMAGE] Converting from mode {resized_image.mode} to RGB")
                 background = Image.new("RGB", resized_image.size, (255, 255, 255))
                 try:
                     mask = None
                     if resized_image.mode == 'RGBA':
                         mask = resized_image.split()[3]
                     elif resized_image.mode == 'LA':
                          mask = resized_image.split()[1] # Alpha is the second channel in LA
                     elif resized_image.mode == 'P' and 'transparency' in resized_image.info:
                          # Handle transparency in Palette mode
                          try:
                             # Attempt to convert to RGBA to get a mask
                              mask = resized_image.convert('RGBA').split()[3]
                          except Exception as conv_err:
                               self.logger.warning(f"[IMAGE] Could not get alpha mask from P mode: {conv_err}")

                     background.paste(resized_image, mask=mask)
                 except IndexError: 
                     self.logger.warning("[IMAGE] Index error getting mask, pasting without mask.")
                     background.paste(resized_image)
                 except Exception as paste_err: 
                     self.logger.error(f"[IMAGE] Error during RGBA/LA/P conversion pasting: {paste_err}, using direct convert.")
                     try:
                        background = resized_image.convert("RGB") # Fallback to direct conversion
                     except Exception as convert_err:
                         self.logger.error(f"[IMAGE] Fallback RGB conversion failed: {convert_err}")
                         # Keep original if all fails (though unlikely to be saveable as JPEG)
                         background = resized_image 
                 resized_image = background

            # 3. Iterative Compression to meet target size
            compressed_image = resized_image
            current_quality = initial_quality
            compressed_size_kb = original_size_kb # Start with original size for loop condition
            last_successful_image = resized_image # Keep track of the last image successfully saved
            last_successful_size_kb = original_size_kb

            while True:
                saved_successfully = False
                current_loop_size_kb = -1.0 # Reset for this loop iteration
                with io.BytesIO() as buffer:
                    try:
                        compressed_image.save(buffer, format="JPEG", quality=current_quality, optimize=True)
                        buffer.seek(0)
                        compressed_data = buffer.getvalue()
                        current_loop_size_kb = len(compressed_data) / 1024
                        saved_successfully = True
                         # Load the image from the buffer of the successful save
                        buffer.seek(0)
                        # Ensure we make a copy to work with outside the buffer's context
                        last_successful_image = Image.open(buffer).copy()
                        last_successful_size_kb = current_loop_size_kb

                    except Exception as save_err:
                         self.logger.error(f"[IMAGE] Error saving JPEG with quality {current_quality}: {save_err}")
                         # Break the loop on save error, will return the last *successful* save
                         break

                self.logger.info(f"[IMAGE] Compression attempt: Quality={current_quality}, Size={current_loop_size_kb:.1f}KB")

                # Check if target met or quality too low
                if current_loop_size_kb <= target_kb or current_quality <= min_quality:
                     break # Exit loop, use last_successful_image

                # Reduce quality for next iteration
                quality_step = 15 if current_loop_size_kb > target_kb * 2 else 10
                current_quality = max(min_quality, current_quality - quality_step)
                
                # Prepare the image for the next iteration - use the last successfully saved image data
                compressed_image = last_successful_image

            # Return the last image that was successfully saved and its size
            return last_successful_image, original_size_kb, last_successful_size_kb

        except Exception as e:
             self.logger.error(f"[IMAGE] Error during compression process: {e}")
             # Fallback: return original image data and size (if calculable)
             return image_data, original_size_kb, original_size_kb

    def _add_assistant_identifier(self, image_data: Image.Image) -> Image.Image:
        """Adds a pixel pattern to identify the image as assistant-generated."""
        try:
            # Ensure image is not animated and is suitable for pixel manipulation
            is_animated = getattr(image_data, 'is_animated', False) or getattr(image_data, 'n_frames', 1) > 1
            if not is_animated and image_data.width > 5 and image_data.height > 5:
                 img_copy = image_data.copy()
                 if img_copy.mode != "RGB":
                      # Attempt conversion to RGB if not already
                      try:
                         img_copy = img_copy.convert("RGB")
                      except Exception as conv_err:
                           self.logger.warning(f"[IMAGE] Could not convert image to RGB for identifier: {conv_err}")
                           return image_data # Return original if conversion fails
                 
                 pixels = img_copy.load()
                 if pixels is not None:
                      # Specific pattern: 3 pixels in bottom-right corner
                      pixels[img_copy.width - 1, img_copy.height - 1] = (250, 250, 253)
                      pixels[img_copy.width - 2, img_copy.height - 1] = (250, 250, 252)
                      pixels[img_copy.width - 1, img_copy.height - 2] = (250, 250, 251)
                      self.logger.info("[IMAGE] Added assistant image identifier pattern")
                      return img_copy # Return the modified copy
            
            # If conditions not met or pixels is None, return original image
            return image_data 

        except Exception as e:
            self.logger.error(f"[IMAGE] Error adding assistant identifier: {str(e)}")
            return image_data # Return original image even if identifier adding failed

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

        async def tool_search_pdf(query: str) -> str:
            """
            Search for information in PDFs stored in the knowledge base.

            Args:
                query (str): The search query to find relevant information in PDF documents

            Returns:
                str: JSON string containing the search results with PDF content or a message indicating no results were found
            """
            self.logger.info(f"[PDF SEARCH] Searching for: {query}")
            knowledge_result = await self.search_knowledge(query)

            if (
                knowledge_result is None
                or knowledge_result.object is None
                or knowledge_result.object.name is None
                or knowledge_result.object.bucket_id is None
            ):
                self.logger.warning(f"[PDF SEARCH] No results found for query: {query}")
                return "Geen PDF gevonden"

            self.logger.info(f"[PDF SEARCH] Found PDF: {knowledge_result.object.name}")

            # Verwerk de afbeeldingen, als die beschikbaar zijn
            images_data = []
            if hasattr(knowledge_result, "images") and knowledge_result.images:
                self.logger.info(f"[PDF SEARCH] Found {len(knowledge_result.images)} images in PDF")
                for img in knowledge_result.images:
                    images_data.append(
                        {
                            "id": img.id,
                            "object_id": img.object_id,
                            "summary": img.summary,
                            "file_name": img.original_file_name,
                            "page": img.page,
                        }
                    )

            # Maak een volledige JSON respons met alle beschikbare informatie
            return json.dumps(
                {
                    "id": knowledge_result.id,
                    "markdown_content": knowledge_result.markdown_content,
                    "title": knowledge_result.object.name,
                    "summary": knowledge_result.short_summary,
                    "long_summary": knowledge_result.long_summary,
                    "images": images_data,
                }
            )

        async def tool_load_image(_id: str, file_name: str) -> Image.Image:
            """
            Loads an image from the database, optimizes it for display, and adds an identifier.
            Handles various image formats including HEIC, applies compression, and ensures
            robustness against errors during processing.

            Args:
                _id (str): The ID associated with the image's source (e.g., PDF ID).
                file_name (str): The filename of the image (can include path components).

            Returns:
                Image.Image: The processed and optimized PIL Image object.

            Raises:
                Exception: If the image cannot be loaded or processed after multiple attempts.
            """
            self.logger.info(f"[IMAGE] Processing request for image '{file_name}' from source ID '{_id}'")

            try:
                # 1. Attempt to load the image using various path formats
                image_data = await self._attempt_load_image(_id, file_name)
                if image_data is None:
                    # If loading failed after trying all paths, raise an error
                    raise FileNotFoundError(f"Could not load image '{file_name}' from source '{_id}' using any known path format.")

                # 2. Handle HEIC conversion if necessary
                image_data = self._convert_heic_to_jpeg(image_data)

                # 3. Apply compression and resizing
                compressed_image, original_size_kb, compressed_size_kb = self._apply_compression(image_data)

                # 4. Add the assistant identifier pattern
                final_image = self._add_assistant_identifier(compressed_image)

                self.logger.info(
                     f"[IMAGE] Optimization complete for '{file_name}': "
                     f"{original_size_kb:.1f}KB -> {compressed_size_kb:.1f}KB "
                     f"(Dimensions: {final_image.width}x{final_image.height})"
                )
                self.logger.info(f"[IMAGE] ASSISTANT IMAGE CREATED: {file_name}")

                # Return the final PIL Image object directly
                return final_image

            except FileNotFoundError as fnf_error:
                 self.logger.error(f"[IMAGE] File not found error: {str(fnf_error)}")
                 # Re-raise specific error for clarity upstream if needed
                 raise fnf_error
            except Exception as e:
                # Catch any other unexpected errors during the process
                self.logger.error(f"[IMAGE] Unexpected error processing image '{file_name}': {str(e)}")
                # Re-raise the exception to signal failure
                raise e

        def tool_example_chart() -> Chart:
            """
            Create an example chart.
            """
            data = [
                {"month": "Jan", "sales": 120},
                {"month": "Feb", "sales": 150},
                {"month": "Mar", "sales": 180},
                {"month": "Apr", "sales": 170},
                {"month": "May", "sales": 200},
            ]

            chart = Chart.create_bar_chart(
                title="Monthly Sales",
                description="2024 Sales Data",
                data=data,
                x_key="month",
                y_keys=["sales"],
                height=400,
            )

            return chart

        tools = [
            tool_store_memory,
            tool_get_easylog_data,
            tool_generate_monthly_report,
            tool_get_object_history,
            tool_search_pdf,
            tool_load_image,
            tool_clear_memories,
            Chart.create_bar_chart,
            Chart.create_line_chart,
            Chart.create_pie_chart,
            tool_example_chart,
        ]

        # Print alle tools om te debuggen
        self.logger.info("All tools before filtering:")
        for tool in tools:
            self.logger.info(f" - {tool.__name__}")

        # Zet alle tools om naar het Anthropic formaat en filter debug tools
        anthropic_tools = []
        for tool in tools:
            if tool.__name__ in [
                "tool_store_memory",
                "tool_get_easylog_data",
                "tool_generate_monthly_report",
                "tool_get_object_history",
                "tool_search_pdf",
                "tool_load_image",
                "tool_clear_memories",
                "create_bar_chart",
                "create_line_chart",
                "create_pie_chart",
                "tool_example_chart",
            ]:
                anthropic_tools.append(function_to_anthropic_tool(tool))
                self.logger.info(f"Added tool to Anthropic tools: {tool.__name__}")
            else:
                self.logger.warning(f"Skipping tool: {tool.__name__}")

        # Print alle tools na filtering om te debuggen
        self.logger.info("All tools after filtering:")
        for i, tool in enumerate(anthropic_tools):
            try:
                if hasattr(tool, "function") and hasattr(tool.function, "name"):
                    self.logger.info(f" - {i + 1}: {tool.function.name}")
                elif isinstance(tool, dict) and "function" in tool and "name" in tool["function"]:
                    self.logger.info(f" - {i + 1}: {tool['function']['name']}")
                else:
                    self.logger.info(f" - {i + 1}: {str(tool)[:50]}")
            except Exception as e:
                self.logger.warning(f" - {i + 1}: Error logging tool: {str(e)}")

        start_time = time.time()

        # In plaats van de stream direct door te geven,
        # bufferen we het volledige antwoord en sturen het dan in één keer.
        stream = await self.client.messages.create(
            # Gebruik Claude 3.7 Sonnet model
            model="claude-3-7-sonnet-20250219",
            max_tokens=2048,
            system=f"""Je bent een vriendelijke en behulpzame data-analist voor EasyLog.
Je taak is om gebruikers te helpen bij het analyseren van bedrijfsgegevens en het maken van overzichtelijke verslagen.

### BELANGRIJKE REGELS:
+- Hou je antwoorden **kort en bondig**. Ga niet onnodig in op details tenzij de gebruiker er expliciet om vraagt.
+- Vat de resultaten van tools **beknopt** samen. Geef alleen de belangrijkste informatie.
- Geef nauwkeurige en feitelijke samenvattingen van de EasyLog data!!
- Help de gebruiker patronen te ontdekken in de controlegegevens
- Maak verslagen in tabellen en duidelijk en professioneel met goede opmaak
- Gebruik grafieken en tabellen waar mogelijk (markdown)
- Wees proactief in het suggereren van analyses die nuttig kunnen zijn

### Beschikbare tools:
- tool_get_easylog_data: Haalt de laatste controles op uit de EasyLog database
- tool_generate_monthly_report: Maakt een maandrapport met statistieken
- tool_get_object_history: Haalt de geschiedenis van een specifiek object op
- tool_store_memory: Slaat belangrijke informatie op voor later gebruik
- tool_clear_memories: Wist alle opgeslagen herinneringen
- tool_search_pdf: Zoek een PDF in de kennisbank
- create_bar_chart: Maakt een staafdiagram van de gegeven data.
- create_line_chart: Maakt een lijndiagram van de gegeven data.
- create_pie_chart: Maakt een cirkeldiagram van de gegeven data.
- tool_example_chart: Genereert een voorbeeld staafdiagram.

### Gebruik van de tool_search_pdf
Je kunt de tool_search_pdf gebruiken om te zoeken in PDF-documenten die zijn opgeslagen in de kennisbank. Gebruik deze tool wanneer een gebruiker vraagt naar informatie die mogelijk in een handboek, rapport of ander PDF-document staat.

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

        # Stuur content direct door
        async for content in self.handle_stream(stream, tools):
            yield content
