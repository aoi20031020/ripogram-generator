"""
English Lipogram Generator CLI using BERT + WordNet approach.
"""

import argparse
import sys
from typing import List
from .core.english_bert_rewriter import EnglishBertRewriter


class EnglishLipogramCLI:
    """Command-line interface for English lipogram generation."""

    def __init__(self):
        """Initialize the CLI."""
        self.rewriter = None

    def initialize_rewriter(self, model_name: str = "bert-base-uncased"):
        """
        Initialize the BERT rewriter.

        Args:
            model_name: BERT model name
        """
        print(f"🔄 Initializing BERT model: {model_name}")
        try:
            self.rewriter = EnglishBertRewriter(model_name)
            print("✅ BERT model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading BERT model: {e}")
            sys.exit(1)

    def generate_lipogram(
        self,
        text: str,
        banned_chars: List[str],
        similarity_threshold: float = 0.5,
        verbose: bool = False
    ) -> str:
        """
        Generate lipogram from input text.

        Args:
            text: Input text
            banned_chars: List of banned characters
            similarity_threshold: Minimum similarity threshold
            verbose: Whether to show detailed output

        Returns:
            Generated lipogram text
        """
        if not self.rewriter:
            raise RuntimeError(
                "Rewriter not initialized. Call initialize_rewriter() first.")

        print(f"\n📝 Input text: {text}")
        print(f"🚫 Banned characters: {', '.join(banned_chars)}")
        print(f"📊 Similarity threshold: {similarity_threshold}")
        print("=" * 60)

        result = self.rewriter.rewrite_text(
            text, banned_chars, similarity_threshold, verbose
        )

        print("=" * 60)
        print(f"✨ Generated lipogram: {result}")

        # Verify result
        banned_found = []
        for char in banned_chars:
            if char.lower() in result.lower():
                banned_found.append(char)

        if banned_found:
            print(
                f"⚠️  Warning: Result still contains banned characters: {', '.join(banned_found)}")
        else:
            print("✅ Success: No banned characters found in result")

        return result

    def interactive_mode(self):
        """Run interactive mode for lipogram generation."""
        print("🎯 English Lipogram Generator (BERT + WordNet)")
        print("=" * 50)

        # Get model preference
        model_choice = input(
            "Choose BERT model (1: bert-base-uncased, 2: bert-large-uncased, 3: custom): ").strip()

        if model_choice == "2":
            model_name = "bert-large-uncased"
        elif model_choice == "3":
            model_name = input("Enter custom model name: ").strip()
        else:
            model_name = "bert-base-uncased"

        self.initialize_rewriter(model_name)

        while True:
            print("\n" + "=" * 50)
            print("Enter your text (or 'quit' to exit):")
            text = input("> ").strip()

            if text.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break

            if not text:
                print("❌ Please enter some text.")
                continue

            # Get banned characters
            print("\nEnter banned characters (space-separated):")
            banned_input = input("> ").strip()

            if not banned_input:
                print("❌ Please enter at least one banned character.")
                continue

            banned_chars = banned_input.split()

            # Get similarity threshold
            threshold_input = input(
                "Enter similarity threshold (0.0-1.0, default 0.5): ").strip()
            try:
                similarity_threshold = float(
                    threshold_input) if threshold_input else 0.5
                similarity_threshold = max(0.0, min(1.0, similarity_threshold))
            except ValueError:
                similarity_threshold = 0.5
                print("⚠️  Invalid threshold, using default 0.5")

            # Get verbosity preference
            verbose_input = input(
                "Show detailed output? (y/n, default n): ").strip().lower()
            verbose = verbose_input in ['y', 'yes', 'true', '1']

            try:
                self.generate_lipogram(
                    text, banned_chars, similarity_threshold, verbose)
            except Exception as e:
                print(f"❌ Error generating lipogram: {e}")

    def run_cli(self):
        """Run the command-line interface."""
        parser = argparse.ArgumentParser(
            description="English Lipogram Generator using BERT + WordNet",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python -m ripogram.english_cli --text "The cat sat on the mat" --banned e a
  python -m ripogram.english_cli --interactive
  python -m ripogram.english_cli --text "Hello world" --banned l o --threshold 0.7 --verbose
            """
        )

        parser.add_argument(
            "--text", "-t",
            type=str,
            help="Input text to convert to lipogram"
        )

        parser.add_argument(
            "--banned", "-b",
            nargs="+",
            help="List of banned characters"
        )

        parser.add_argument(
            "--model", "-m",
            type=str,
            default="bert-base-uncased",
            help="BERT model name (default: bert-base-uncased)"
        )

        parser.add_argument(
            "--threshold", "-th",
            type=float,
            default=0.5,
            help="Similarity threshold (0.0-1.0, default: 0.5)"
        )

        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Show detailed processing output"
        )

        parser.add_argument(
            "--interactive", "-i",
            action="store_true",
            help="Run in interactive mode"
        )

        args = parser.parse_args()

        if args.interactive:
            self.interactive_mode()
        elif args.text and args.banned:
            # Validate threshold
            threshold = max(0.0, min(1.0, args.threshold))

            self.initialize_rewriter(args.model)
            self.generate_lipogram(
                args.text, args.banned, threshold, args.verbose)
        else:
            parser.print_help()
            print(
                "\n❌ Error: Either use --interactive or provide both --text and --banned")
            sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli = EnglishLipogramCLI()
    cli.run_cli()


if __name__ == "__main__":
    main()
