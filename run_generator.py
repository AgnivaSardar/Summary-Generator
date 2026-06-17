import argparse
import sys
from config.settings import settings
from services.patient_summary_service import PatientSummaryService


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI Clinical Synopsis and update backend."
    )
    parser.add_argument(
        "--patient",
        required=True,
        help="The Patient ID to generate the summary for."
    )
    parser.add_argument(
        "--company",
        default=settings.DEFAULT_COMPANY_ID,
        help=f"The Company ID (default: {settings.DEFAULT_COMPANY_ID})."
    )

    args = parser.parse_args()

    print(f"Generating summary for patient: {args.patient}, company: {args.company}...")

    try:
        service = PatientSummaryService()
        result = service.generate(
            patient_id=args.patient,
            company_id=args.company
        )
        print("\n" + "=" * 50)
        print("GENERATED CLINICAL SYNOPSIS:")
        print("=" * 50)
        print(result["summary"])
        print("=" * 50)
        print(f"\nBackend updated successfully for patient ID {args.patient}.")

    except Exception as e:
        print(f"\n[ERROR] Generation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
