import requests
import threading
import time
from datetime import datetime

BASE_API_URL = "http://127.0.0.1:5000/check_domain"
DOMAINS_TO_CHECK = ["google.com", "idekerenbanget.com", "tokopedia.com", "startupimpianku.id", "github.com"]
NUM_REQUESTS = len(DOMAINS_TO_CHECK)
CLIENT_LOG_FILE = "domain_checker_log.txt"

client_log_lock = threading.Lock()

with open(CLIENT_LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"--- Domain Checker Log Started: {datetime.now()} ---\n")

# ==============================================================================
# SOAL 1: Implementasi Logging Thread-Safe
# ==============================================================================
def log_client_activity_safe(thread_name, message):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    log_message = f"[{timestamp}] [{thread_name}] {message}\n"
    
    with client_log_lock:
        with open(CLIENT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_message)
        print(log_message, end="")

# ==============================================================================
# SOAL 2: Implementasi Fungsi Permintaan API
# ==============================================================================
def request_domain_status_from_api(domain, current_thread_name):

    target_url = f"{BASE_API_URL}?domain={domain}"
    log_client_activity_safe(current_thread_name, f"Mengirim permintaan untuk domain: {domain}")
    
    try:
        response = requests.get(target_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            
            if status == "Available":
                log_client_activity_safe(current_thread_name, 
                    f"TERSEDIA! Domain {data.get('domain', domain)} bisa didaftarkan.")
            elif status == "Registered":
                log_client_activity_safe(current_thread_name,
                    f"TERDAFTAR! Domain {data.get('domain', domain)} sudah dimiliki.")
            else:
                log_client_activity_safe(current_thread_name,
                    f"Status tidak dikenali untuk domain {domain}: {status}")
        else:
            log_client_activity_safe(current_thread_name,
                f"Menerima status error dari API: {response.status_code} - {response.text[:100]}")
                
    except requests.exceptions.Timeout:
        log_client_activity_safe(current_thread_name,
            f"Timeout saat memeriksa domain {domain}")
    except requests.exceptions.RequestException as e:
        log_client_activity_safe(current_thread_name,
            f"Error permintaan untuk domain {domain}: {str(e)}")
    except Exception as e:
        log_client_activity_safe(current_thread_name,
            f"Kesalahan tak terduga saat memeriksa domain {domain}: {str(e)}")
    
    log_client_activity_safe(current_thread_name, f"Tugas untuk domain {domain} selesai.")

def worker_thread_task(domain, task_id):
    """Fungsi yang dijalankan oleh setiap worker thread."""
    thread_name = f"Worker-{task_id}"
    log_client_activity_safe(thread_name, f"Memulai pengecekan untuk domain: {domain}")
    request_domain_status_from_api(domain, thread_name)
    log_client_activity_safe(thread_name, f"Selesai pengecekan untuk domain: {domain}")

if __name__ == "__main__":
    log_client_activity_safe("MainClient", f"Memulai {NUM_REQUESTS} pengecekan ketersediaan domain secara concurrent.")
    
    threads = []
    start_time = time.time()

    for i, domain_name in enumerate(DOMAINS_TO_CHECK):
        thread = threading.Thread(target=worker_thread_task, args=(domain_name, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    total_time = end_time - start_time
    
    log_client_activity_safe("MainClient", f"Semua pengecekan domain selesai dalam {total_time:.2f} detik.")
    print(f"\nLog aktivitas klien disimpan di: {CLIENT_LOG_FILE}")
    print(f"Total waktu eksekusi: {total_time:.2f} detik.")


