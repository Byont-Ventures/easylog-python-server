# Python standard library imports
import asyncio
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
from src.utils.function_to_anthropic_tool import function_to_anthropic_tool

# Load all variables from .env
load_dotenv()


class HealthData(TypedDict):
    """
    Defines the structure for health data
    """
    date: str
    activity: str
    duration: int
    intensity: str
    symptoms: list[str]


# Configuration class for AnthropicHealth agent
class AnthropicHealthAgentConfig(BaseModel):
    max_history_entries: int = Field(
        default=50,
        description="Maximum number of entries to fetch from the database for health history!",
    )
    debug_mode: bool = Field(
        default=True, description="Enable debug mode with additional logging"
    )
    image_max_width: int = Field(
        default=1200, description="Maximum width for processed images in pixels"
    )
    image_quality: int = Field(
        default=90, description="JPEG quality for processed images (1-100)"
    )


# Agent class that integrates with Anthropic's Claude API for health coaching
class AnthropicHealthAgent(AnthropicAgent[AnthropicHealthAgentConfig]):
    def __init__(self, *args, **kwargs) -> None:
        # Call the parent class init
        super().__init__(*args, **kwargs)

        # Extra logging to track tools
        self.available_tools = []
        self.logger.info("HealthAgent initialized with health coaching tools")

        # Disable debug mode to avoid loading debug tools
        self.config.debug_mode = False

    def _describe_available_tools(self):
        """Log available tools in the class and filter out debug tools"""
        all_tools = [
            "tool_store_memory",
            "tool_search_pdf",
            "tool_load_image",
            "tool_clear_memories",
        ]

        self.available_tools = all_tools
        self.logger.info(f"Available tools for HealthAgent: {', '.join(all_tools)}")

    def _extract_user_info(self, message_text: str) -> list[str]:
        """
        Automatically detects important information in the user's message!!

        Args:
            message_text: The text content of the user's message

        Returns:
            A list of detected information
        """
        detected_info = []

        # Detect names
        name_patterns = [
            r"(?i)(?:ik ben|mijn naam is|ik heet|noem mij)\s+([A-Za-z\s]+)",
            r"(?i)naam(?:\s+is)?\s+([A-Za-z\s]+)",
        ]

        for pattern in name_patterns:
            matches = re.findall(pattern, message_text)
            for match in matches:
                name = match.strip()
                if name and len(name) > 1:  # Minimum length to avoid false positives
                    detected_info.append(f"Naam: {name}")
                    self.logger.info(f"Detected user name: {name}")

        # Detect age
        age_patterns = [
            r"(?i)(?:ik ben|leeftijd is)\s+(\d{1,3})\s+(?:jaar|jaar oud)",
            r"(?i)(?:leeftijd|jaar)(?:\s+is)?\s+(\d{1,3})",
        ]

        for pattern in age_patterns:
            matches = re.findall(pattern, message_text)
            for match in matches:
                age = match.strip()
                if age and 1 <= int(age) <= 120:  # Valid age range
                    detected_info.append(f"Leeftijd: {age}")
                    self.logger.info(f"Detected user age: {age}")

        # Detect health conditions
        condition_patterns = [
            r"(?i)(?:ik heb|gediagnosticeerd met|last van)\s+(COPD|astma|diabetes|hartproblemen|hoge bloeddruk|allergie|artrose|copd)",
            r"(?i)(?:ziekte|aandoening)(?:\s+is)?\s+(COPD|astma|diabetes|hartproblemen|hoge bloeddruk|allergie|artrose|copd)",
        ]

        for pattern in condition_patterns:
            matches = re.findall(pattern, message_text)
            for match in matches:
                condition = match.strip()
                if condition and len(condition) > 2:  # Minimum length to avoid false positives
                    detected_info.append(f"Aandoening: {condition}")
                    self.logger.info(f"Detected health condition: {condition}")

        # Detect exercise preferences
        exercise_patterns = [
            r"(?i)(?:ik hou van|doe graag|vind leuk)\s+([A-Za-z\s]+(?:wandelen|fietsen|zwemmen|yoga|fitness|pilates|sport))",
            r"(?i)(?:sport|beweging|activiteit)(?:\s+is)?\s+([A-Za-z\s]+)",
        ]

        for pattern in exercise_patterns:
            matches = re.findall(pattern, message_text)
            for match in matches:
                activity = match.strip()
                if activity and len(activity) > 3:  # Minimum length to avoid false positives
                    detected_info.append(f"Activiteit: {activity}")
                    self.logger.info(f"Detected exercise preference: {activity}")

        return detected_info

    async def _store_detected_name(self, message_text: str):
        """
        Detects and stores important information from the user's message

        Args:
            message_text: The text content of the user's message
        """
        detected_info = self._extract_user_info(message_text)

        if not detected_info:
            return

        # Directly call store_memory for each detected piece of information
        for info in detected_info:
            await self._store_memory_internal(info)

    async def _store_memory_internal(self, memory: str):
        """
        Internal function to store memories with duplicate checking

        Args:
            memory: The memory to be stored
        """
        memory = memory.strip()
        if not memory:
            return

        # Get current memories
        current_memories = self.get_metadata("memories", default=[])

        # Extract type (everything before the first ":")
        memory_type = memory.split(":", 1)[0].strip().lower() if ":" in memory else ""

        # Look for existing memory of the same type
        existing_index = -1
        for i, existing_memory in enumerate(current_memories):
            existing_type = (
                existing_memory.split(":", 1)[0].strip().lower()
                if ":" in existing_memory
                else ""
            )
            if memory_type and existing_type == memory_type:
                existing_index = i
                break

        # Update existing or add new memory
        if existing_index >= 0:
            # Replace existing memory
            current_memories[existing_index] = memory
            self.logger.info(f"Updated existing memory: {memory}")
        else:
            # Add new memory
            current_memories.append(memory)
            self.logger.info(f"Added new memory: {memory}")

        # Store updated memories
        self.set_metadata("memories", current_memories)

    async def on_message(
        self, messages: list[Message]
    ) -> AsyncGenerator[MessageContent, None]:
        """
        This function handles each message from the user.
        We buffer the complete Claude response signal, so base64 images 
        come through all at once (and not partially) with slow connections.
        """
        # Remove any debug tools that might still be in the code
        self.logger.info("Removing any debug tools that might still be in code")
        # Remove debug mode debug tools
        self.config.debug_mode = False

        # Describe available tools
        self._describe_available_tools()

        # Log the incoming message for debugging
        if messages and len(messages) > 0:
            last_message = messages[-1]
            if last_message.role == "user" and isinstance(last_message.content, str):
                self.logger.info(
                    f"Processing user message: {last_message.content[:100]}..."
                )
                # Automatically detect and store name
                await self._store_detected_name(last_message.content)

        # Convert messages to a format Claude understands
        message_history = self._convert_messages_to_anthropic_format(messages)

        if self.config.debug_mode:
            self.logger.debug(f"Converted message history: {message_history}")

        # Retrieve memories
        memories = self.get_metadata("memories", default=[])
        logger.info(f"Current memories: {memories}")

        def tool_clear_memories():
            """
            Clear all stored memories and conversation history.
            """
            self.set_metadata("memories", [])
            message_history.clear()
            self.logger.info("Memories and conversation history cleared")
            return "All memories and conversation history have been cleared."

        async def tool_store_memory(memory: str) -> str:
            """
            Store a memory in the database.
            """
            current_memory = self.get_metadata("memories", default=[])
            current_memory.append(memory)
            self.logger.info(f"Storing memory: {memory}")
            self.set_metadata("memories", current_memory)
            return "Memory stored"

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
                return "No PDF found"

            self.logger.info(f"[PDF SEARCH] Found PDF: {knowledge_result.object.name}")

            # Process images if available
            images_data = []
            if hasattr(knowledge_result, "images") and knowledge_result.images:
                self.logger.info(
                    f"[PDF SEARCH] Found {len(knowledge_result.images)} images in PDF"
                )
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

            # Create a complete JSON response with all available information
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
            Load an image from the database and prepare it for display.
            The function accepts both full paths (figures/file.png) and just filenames (file.png).

            Args:
                _id (str): The ID of the PDF file
                file_name (str): The filename of the image (with or without path)

            Returns:
                str: A data URL with the image as base64 encoded data
            """
            self.logger.info(f"[IMAGE] Loading image {file_name} from {_id}")

            try:
                # Simplified path logic: try different path formats until one works
                possible_paths = [
                    file_name,
                    f"figures/{file_name}" if "/" not in file_name else file_name,
                    file_name.replace("figures/", "")
                    if file_name.startswith("figures/")
                    else file_name,
                    file_name.split("/")[-1],  # Just the filename
                ]

                # Try each possible path variant
                image_data = None
                last_error = None
                max_retries = 2  # Number of times to retry loading on network errors

                for path in possible_paths:
                    retry_count = 0
                    while retry_count <= max_retries and image_data is None:
                        try:
                            image_data = await self.load_image(_id, path)
                            self.logger.info(
                                f"[IMAGE] Successfully loaded with path: {path}"
                            )
                            break
                        except Exception as e:
                            last_error = e
                            retry_count += 1
                            if retry_count <= max_retries:
                                self.logger.warning(
                                    f"[IMAGE] Attempt {retry_count} failed, trying again..."
                                )
                                # Short pause before next attempt
                                await asyncio.sleep(0.5)

                    if image_data is not None:
                        break

                if image_data is None:
                    raise last_error or Exception(
                        "Could not load image with available paths"
                    )

                # Validate that we have a valid image
                if not hasattr(image_data, "size") or not image_data.size:
                    raise ValueError("Invalid image data received")

                # Determine original size
                with io.BytesIO() as buffer:
                    image_data.save(buffer, format=image_data.format or "PNG")
                    buffer.seek(0)
                    original_size = len(buffer.getvalue())
                    original_size_kb = original_size / 1024

                # Simplified compression logic
                original_width, original_height = image_data.size

                # Basic configuration for optimal performance on mobile devices
                max_width = 600
                quality = 60

                # Simple adjustment based on image size
                if original_size < 100 * 1024:  # < 100 KB
                    max_width = min(original_width, 800)
                    quality = 75
                elif original_size > 1 * 1024 * 1024:  # > 1 MB
                    max_width = 450
                    quality = 45

                # For very poor connections: even smaller and more compressed
                if original_size > 2 * 1024 * 1024:  # > 2 MB
                    max_width = 400
                    quality = 35

                # Resize if needed
                if original_width > max_width:
                    scale_factor = max_width / original_width
                    new_height = int(original_height * scale_factor)
                    image_data = image_data.resize(
                        (max_width, new_height), Image.Resampling.LANCZOS
                    )

                # Convert to RGB (for images with transparency)
                if image_data.mode in ("RGBA", "LA"):
                    background = Image.new("RGB", image_data.size, (255, 255, 255))
                    background.paste(
                        image_data,
                        mask=image_data.split()[3]
                        if len(image_data.split()) > 3
                        else None,
                    )
                    image_data = background

                # Compress the image
                compressed_data = None
                for attempt in range(2):  # Multiple attempts to compress
                    try:
                        with io.BytesIO() as buffer:
                            image_data.save(
                                buffer, format="JPEG", quality=quality, optimize=True
                            )
                            buffer.seek(0)
                            compressed_data = buffer.getvalue()
                            if compressed_data:  # Check if we have valid data
                                break
                    except Exception as e:
                        self.logger.warning(
                            f"[IMAGE] Compression attempt {attempt + 1} failed: {e}"
                        )
                        quality -= 10  # Lower quality on next attempt

                if not compressed_data:
                    raise ValueError("Could not compress image")

                compressed_size = len(compressed_data)
                compressed_size_kb = compressed_size / 1024

                # Extra compression only if really needed (> 150KB)
                if compressed_size > 150 * 1024:
                    # Further reduce size and compress
                    new_width = int(image_data.width * 0.7)
                    new_height = int(image_data.height * 0.7)

                    image_data = image_data.resize(
                        (new_width, new_height), Image.Resampling.LANCZOS
                    )

                    # Try blurring for better compression
                    try:
                        from PIL import ImageFilter

                        image_data = image_data.filter(
                            ImageFilter.GaussianBlur(radius=0.6)
                        )
                    except Exception:
                        pass

                    with io.BytesIO() as buffer:
                        image_data.save(
                            buffer, format="JPEG", quality=40, optimize=True
                        )

                self.logger.info(
                    f"[IMAGE] Image optimized: {original_size_kb:.1f}KB → {compressed_size_kb:.1f}KB"
                )
                return image_data

            except Exception as e:
                self.logger.error(f"[IMAGE] Error during processing: {str(e)}")
                raise e

        tools = [
            tool_store_memory,
            tool_search_pdf,
            tool_load_image,
            tool_clear_memories,
        ]

        # Print all tools for debugging
        self.logger.info("All tools before filtering:")
        for tool in tools:
            self.logger.info(f" - {tool.__name__}")

        # Convert all tools to Anthropic format and filter debug tools
        anthropic_tools = []
        for tool in tools:
            if tool.__name__ in [
                "tool_store_memory",
                "tool_search_pdf",
                "tool_load_image",
                "tool_clear_memories",
            ]:
                anthropic_tools.append(function_to_anthropic_tool(tool))
                self.logger.info(f"Added tool to Anthropic tools: {tool.__name__}")
            else:
                self.logger.warning(f"Skipping tool: {tool.__name__}")

        # Print all tools after filtering for debugging
        self.logger.info("All tools after filtering:")
        for i, tool in enumerate(anthropic_tools):
            try:
                if hasattr(tool, "function") and hasattr(tool.function, "name"):
                    self.logger.info(f" - {i + 1}: {tool.function.name}")
                elif (
                    isinstance(tool, dict)
                    and "function" in tool
                    and "name" in tool["function"]
                ):
                    self.logger.info(f" - {i + 1}: {tool['function']['name']}")
                else:
                    self.logger.info(f" - {i + 1}: {str(tool)[:50]}")
            except Exception as e:
                self.logger.warning(f" - {i + 1}: Error logging tool: {str(e)}")

        start_time = time.time()

        # Instead of passing the stream directly,
        # we buffer the complete response and then send it at once.
        buffered_content = []
        stream = await self.client.messages.create(
            # Use Claude 3.7 Sonnet model
            model="claude-3-7-sonnet-20250219",
            max_tokens=2048,
            system=f"""You are a friendly and supportive health coach specializing in helping people with COPD.
Your role is to provide personalized guidance, encouragement, and advice to help users manage their condition and improve their quality of life.

### IMPORTANT RULES:
- Be empathetic and understanding of the challenges COPD patients face
- Focus on realistic, achievable goals that match the user's capabilities
- Provide evidence-based advice for managing COPD symptoms
- Emphasize the importance of proper breathing techniques
- Encourage appropriate physical activity tailored to their abilities
- Promote healthy eating habits and proper hydration
- Remind about medication adherence but don't give specific medical advice
- Use positive, motivating language to encourage healthy habits
- Be sensitive to symptoms like shortness of breath, fatigue, and limited mobility

### Available tools:
- tool_store_memory: Stores important information for later use
- tool_clear_memories: Clears all stored memories
- tool_search_pdf: Searches a PDF in the knowledge base
- tool_load_image: Loads images from PDFs to illustrate points

### Using the tool_search_pdf
You can use the tool_search_pdf to search for information in PDF documents stored in the knowledge base. Use this tool when a user asks about information that might be in a handbook, report, or other PDF document.

### Core memories
Core memories are important information you should remember about a user. You collect these yourself with the "store_memory" tool. For example, if the user tells you their name, has experienced an important event, or has provided important information, you should store it in the core memories.

Examples of important memories to store:
- User's name (e.g., "Naam: Jan")
- Age (e.g., "Leeftijd: 67")
- Health conditions (e.g., "Aandoening: COPD stadium 2")
- Activity preferences (e.g., "Activiteit: wandelen")
- Specific needs or limitations (e.g., "Beperking: kortademig bij traplopen")

Your current core memories are:
{"\n- " + "\n- ".join(memories) if memories else " No memories stored"}

### Health coaching tips:
- Suggest breathing exercises to help manage shortness of breath
- Recommend appropriate physical activities based on their abilities
- Provide nutritional advice that supports respiratory health
- Offer strategies for energy conservation
- Share stress management techniques
- Encourage regular checkups with healthcare providers
- Remind about the importance of avoiding respiratory irritants
- Suggest ways to track symptoms and recognize warning signs
            """,
            messages=message_history,
            tools=anthropic_tools,
            stream=True,
        )

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Time taken for API call: {execution_time:.2f} seconds")

        if execution_time > 5.0:
            logger.warning(
                f"API call took longer than expected: {execution_time:.2f} seconds"
            )

        # Detect and buffer all messages with images because they are most sensitive
        # to streaming problems with poor internet connections
        has_image_content = False
        image_buffer = []
        image_chunks = []  # Specifically for images
        text_after_image = []  # For text after images

        async for content in self.handle_stream(stream, tools):
            # Check if we've detected images
            if hasattr(content, "type") and content.type == "image":
                # Image detected, switch to buffer mode
                has_image_content = True
                self.logger.info("Image detected, switching to buffer mode")
                # Add this image to the special image buffer
                image_chunks.append(content)
                image_buffer.append(content)
            elif has_image_content:
                # We've already seen an image
                if hasattr(content, "type") and content.type == "text":
                    # Text after image, keep separate for better recovery
                    text_after_image.append(content)
                    image_buffer.append(content)
                else:
                    # Other content, just buffer
                    image_buffer.append(content)
            else:
                # No images detected, send content directly (smooth streaming)
                yield content

        # Sending buffered content
        if has_image_content:
            # Smart sending logic for images and text
            if len(image_chunks) == 1:
                # Just one image, send as a whole
                self.logger.info(
                    f"Sending complete buffered response with 1 image ({len(image_buffer)} parts)"
                )
                for chunk in image_buffer:
                    yield chunk
            else:
                # Multiple images, send one by one with text in between
                self.logger.info(
                    f"Sending {len(image_chunks)} images with protected buffering"
                )

                current_image_index = 0
                for chunk in image_buffer:
                    if hasattr(chunk, "type") and chunk.type == "image":
                        current_image_index += 1
                        self.logger.info(
                            f"Sending image {current_image_index} of {len(image_chunks)}"
                        )

                    # Send each part with a small pause for better stability
                    yield chunk
                    if hasattr(chunk, "type") and chunk.type == "image":
                        # Short pause after each image to give the client time for processing
                        await asyncio.sleep(0.1) 