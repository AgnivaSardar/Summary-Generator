from models.processor_result import (
    ProcessorResult
)


class PriorityProcessor:

    def process(
        self,
        facts
    ):

        sorted_facts = sorted(

            facts,

            key=lambda x:
            x.priority_score,

            reverse=True
        )

        return ProcessorResult(

            processor_name=
            "PriorityProcessor",

            facts=sorted_facts
        )