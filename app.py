import flask
from flask import Flask, jsonify, request
import time
import random

app = Flask(__name__)

mock_registered_domains = {
    "google.com": {"registrar": "MarkMonitor Inc.", "status": "Registered"},
    "tokopedia.com": {"registrar": "Tokopedia PT", "status": "Registered"},
    "binus.ac.id": {"registrar": "PANDI", "status": "Registered"},
    "github.com": {"registrar": "GitHub Inc.", "status": "Registered"},
    "microsoft.com": {"registrar": "MarkMonitor Inc.", "status": "Registered"},
}

@app.route('/check_domain', methods=['GET'])
def check_domain():
    domain_param = request.args.get('domain')
    delay = random.uniform(0.1, 0.4)
    time.sleep(delay)
    if domain_param:
        domain = domain_param.lower()
        if domain in mock_registered_domains:
            data = mock_registered_domains[domain]
            data["domain"] = domain
            print(f"[SERVER] Sending status for {domain}: {data} (after {delay:.2f}s delay)")
            return jsonify(data)
        else:
            # Jika tidak ada di database kami, kami anggap tersedia
            success_msg = {"status": "Available", "domain": domain, "message": f"Domain '{domain}' appears to be available for registration."}
            print(f"[SERVER] Domain {domain} is available (after {delay:.2f}s delay)")
            return jsonify(success_msg), 200
    else:
        error_msg = {"error": "bad_request", "message": "Parameter 'domain' is required."}
        return jsonify(error_msg), 400

if __name__ == '__main__':
    print("Simple Domain Availability API Server running on http://127.0.0.1:5000")
    print("Endpoint: GET /check_domain?domain=google.com")
    app.run(debug=False, threaded=True, use_reloader=False)