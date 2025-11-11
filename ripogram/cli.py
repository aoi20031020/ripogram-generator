"""
Command-line interface for ripogram generation.
"""

import argparse
import sys
from typing import List
from .config import Config
from .core.rewriter import RipogramRewriter


def parse_banned_chars(banned_chars_str: str) -> List[str]:
    """
    Parse banned characters string into list.
    
    Args:
        banned_chars_str: Comma-separated string of banned characters
        
    Returns:
        List of banned characters
    """
    return [char.strip() for char in banned_chars_str.split(",")]


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Generate Japanese ripograms using OpenAI GPT-4"
    )
    
    parser.add_argument(
        "sentence",
        help="Input Japanese sentence to convert"
    )
    
    parser.add_argument(
        "--banned-chars", "-b",
        type=str,
        required=True,
        help="Comma-separated list of banned characters (e.g., 'さ,い')"
    )
    
    parser.add_argument(
        "--env-file", "-e",
        type=str,
        help="Path to .env file (default: .env in current directory)"
    )
    
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="gpt-4.1-nano",
        help="OpenAI model to use (default: gpt-4.1-nano)"
    )

    parser.add_argument(
        "--mode", "-M",
        type=str,
        choices=["sequential", "oneshot"],
        default="sequential",
        help="Rewriting mode: 'sequential' (token-level) or 'oneshot' (single-pass baseline)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = Config(env_file=args.env_file)
        
        # Override model if specified
        if args.model:
            config.model_name = args.model
        
        # Parse banned characters
        banned_chars = parse_banned_chars(args.banned_chars)
        
        if args.verbose:
            print(f"🔵 元の文: {args.sentence}")
            print(f"🚫 禁止文字: {banned_chars}")
            print(f"🤖 使用モデル: {config.model_name}")
            print("-" * 50)
        
        # Initialize rewriter
        rewriter = RipogramRewriter(
            api_key=config.openai_api_key,
            model_name=config.model_name
        )

        # Process the sentence using the selected mode
        if args.mode == "oneshot":
            result = rewriter.rewrite_text_one_shot(
                text=args.sentence,
                banned_chars=banned_chars,
                verbose=args.verbose
            )
        else:
            result = rewriter.rewrite_text_with_context(
                text=args.sentence,
                banned_chars=banned_chars,
                verbose=args.verbose
            )
        
        if args.verbose:
            print("-" * 50)
            print(f"🟢 変換後: {result}")
        else:
            print(result)
            
    except ValueError as e:
        print(f"❌ Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
