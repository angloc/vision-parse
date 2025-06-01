import argparse
import os
import logging
from vision_parse import VisionParser, VisionParserError, UnsupportedFileError

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Convert PDF documents to markdown using Vision Parse.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input PDF file.")
    parser.add_argument("--output", type=str, required=True, help="Path to save the output markdown file.")
    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("VISION_PARSE_MODEL_NAME", "gpt-4o"), # Default to gpt-4o if not in env
        help="Name of the vision model to use (e.g., 'gpt-4o'). Overrides VISION_PARSE_MODEL_NAME environment variable if set."
    )
    parser.add_argument(
        "--api_key",
        type=str,
        default=os.getenv("OPENAI_API_KEY"),
        help="OpenAI API key. Overrides OPENAI_API_KEY environment variable if set. If not provided here or in .env, the OpenAI library might raise an error."
    )
    parser.add_argument(
        "--base_url",
        type=str,
        default=os.getenv("OPENAI_BASE_URL"),
        help="OpenAI base URL (for custom deployments like cloudrouter). Overrides OPENAI_BASE_URL environment variable if set."
    )
    parser.add_argument(
        "--detailed_extraction",
        action=argparse.BooleanOptionalAction, # Allows --detailed_extraction or --no-detailed_extraction
        default=False,
        help="Enable detailed extraction mode (tables, LaTeX, etc.). Default is False."
    )
    parser.add_argument(
        "--enable_concurrency",
        action=argparse.BooleanOptionalAction,
        default=True, # Defaulting to True as it's generally preferred
        help="Enable concurrent processing of PDF pages. Default is True."
    )

    args = parser.parse_args()

    logger.info(f"Starting PDF to Markdown conversion for: {args.input}")
    logger.info(f"Using model: {args.model}")
    if args.base_url:
        logger.info(f"Using custom OpenAI base URL: {args.base_url}")
    if args.detailed_extraction:
        logger.info("Detailed extraction enabled.")
    if args.enable_concurrency:
        logger.info("Concurrency enabled.")
    else:
        logger.info("Concurrency disabled.")


    # Prepare openai_config if base_url is provided
    openai_config = {}
    if args.base_url:
        openai_config["OPENAI_BASE_URL"] = args.base_url

    # The OpenAI API key can be passed directly to VisionParser.
    # If api_key is None here, and also not set as an environment variable OPENAI_API_KEY,
    # the OpenAI library (used internally by vision-parse) will raise an error.
    # If api_key is provided (either via arg or env var), it will be used.
    # If base_url is provided (either via arg or env var), it will be used via openai_config.

    try:
        # Instantiate VisionParser
        # We pass api_key and openai_config explicitly.
        # If args.api_key is None, it means it wasn't provided as a CLI argument.
        # The os.getenv('OPENAI_API_KEY') in the default value for args.api_key already loaded it if it was in the env.
        # Same logic applies to args.base_url.
        vision_parser = VisionParser(
            model_name=args.model,
            api_key=args.api_key, # This will be None if not in CLI args or .env
            openai_config=openai_config if openai_config else None, # Pass None if empty
            detailed_extraction=args.detailed_extraction,
            enable_concurrency=args.enable_concurrency
            # Other parameters like temperature, top_p can be added as CLI args if needed
        )

        logger.info("VisionParser initialized. Starting PDF conversion...")
        markdown_pages = vision_parser.convert_pdf(args.input)

        logger.info(f"Successfully converted PDF. Saving markdown to: {args.output}")
        with open(args.output, "w", encoding="utf-8") as f:
            for i, page_content in enumerate(markdown_pages):
                f.write(f"--- Page {i+1} ---\n\n")
                f.write(page_content)
                if i < len(markdown_pages) - 1:
                    f.write("\n\n")

        logger.info("Markdown file saved successfully.")

    except UnsupportedFileError as e:
        logger.error(f"Error: {e}. The input file is not a supported PDF.")
    except VisionParserError as e:
        logger.error(f"Error during vision parsing: {e}")
    except FileNotFoundError as e:
        logger.error(f"Error: Input PDF file not found at {args.input}. Details: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True) # exc_info=True for traceback

if __name__ == "__main__":
    main()
