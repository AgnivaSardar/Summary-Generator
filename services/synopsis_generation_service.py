from llm.summary_generator import (
    SummaryGenerator
)


class SynopsisGenerationService:

    def generate(
        self,
        context
    ):

        generator = (
            SummaryGenerator()
        )

        return (
            generator.generate(
                context
            )
        )