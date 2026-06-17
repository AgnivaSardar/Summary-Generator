import os
import json
import requests


def main():
    this_service_base_url = os.getenv(
        "THIS_SERVICE_BASE_URL",
        "http://localhost:8000"
    ).rstrip("/")

    # May contain '/' (e.g. "25/7"). FastAPI route uses path param so we must URL-encode.
    patient_id = os.getenv("PATIENT_ID", "25/7")
    company_id = os.getenv("COMPANY_ID", "00262")

    from urllib.parse import unquote, quote

    # If PATIENT_ID is already encoded, normalize by decoding then encoding exactly once.
    patient_id_normalized = unquote(patient_id)
    patient_id_encoded = quote(patient_id_normalized, safe="")

    url = f"{this_service_base_url}/api/v1/summary/{patient_id_encoded}"
    params = {"company_id": company_id}

    print("Calling summary endpoint:")
    print("  ", url)
    print("  params:", params)

    resp = requests.post(
        url,
        params=params,
        headers={"Accept": "application/json"},
        timeout=180
    )

    print("\nStatus:", resp.status_code)

    try:
        data = resp.json()
        print("\nResponse JSON:\n")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        if isinstance(data, dict) and "summary" in data:
            print("\n===== SUMMARY =====\n")
            print(data["summary"])
    except ValueError:
        print("\nNon-JSON response body:\n")
        print(resp.text)


if __name__ == "__main__":
    main()

