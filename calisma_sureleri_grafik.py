import threading
import time
import matplotlib.pyplot as plt
import psutil
import os
from tqdm import tqdm
import numpy as np

ULTIMATE_MAX_THREAD = 32
ITERATION_COUNT = 100

# Proses önceliğini yükselt
try:
    # Windows için
    import psutil
    process = psutil.Process()
    process.nice(psutil.HIGH_PRIORITY_CLASS)
except:
    try:
        # Unix/Linux için
        os.nice(-20)
    except:
        print("Proses önceliği yükseltilemedi.")

class ThreadArgs:
    def __init__(self, id, batch_number, total_batch):
        self.id = id
        self.batch_number = batch_number
        self.total_batch = total_batch

total = 0
mutex = threading.Lock()

def thread_function(args):
    batch_number = args.batch_number
    total_batch = args.total_batch

    N = 10000000

    batch_size = N // total_batch
    remainder = N % total_batch

    if batch_number <= remainder:
        batch_interval_start = (batch_size + 1) * (batch_number - 1) + 1
        batch_interval_end = batch_interval_start + batch_size + 1
    else:
        batch_interval_start = (batch_size + 1) * remainder + batch_size * (batch_number - remainder - 1) + 1
        batch_interval_end = batch_interval_start + batch_size

    local_sum = 0
    for i in range(batch_interval_start, batch_interval_end):
        local_sum += i

    with mutex:
        global total
        total += local_sum

def run_thread_test(max_threads):
    global total
    total = 0

    threads = []
    for i in range(max_threads):
        args = ThreadArgs(
            id=i,
            batch_number=i + 1,
            total_batch=max_threads
        )

        thread = threading.Thread(target=thread_function, args=(args,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return total

def main():
    thread_counts = list(range(1, ULTIMATE_MAX_THREAD + 1))
    average_runtimes = []

    print("\nTest başlatılıyor...")
    print(f"Her thread sayısı için {ITERATION_COUNT} kez test yapılacak.")

    # Her thread sayısı için progress bar
    for thread_count in tqdm(thread_counts, desc="Thread Sayıları"):
        runtimes = []

        # Her iterasyon için
        for _ in range(ITERATION_COUNT):
            start_time = time.perf_counter_ns()
            run_thread_test(thread_count)
            end_time = time.perf_counter_ns()
            elapsed_time = (end_time - start_time) / 1e9  # Saniyeye çevirme
            runtimes.append(elapsed_time)

        # Ortalama runtime'ı hesapla
        avg_runtime = np.mean(runtimes)
        average_runtimes.append(avg_runtime)

    print("\nGörselleştirme oluşturuluyor...")

    # Scatter plot oluşturma
    plt.figure(figsize=(12, 8))

    # Ana scatter plot
    plt.scatter(thread_counts, average_runtimes, c='blue', alpha=0.6, label='Ortalama Çalışma Süresi')

    # Trend çizgisi
    z = np.polyfit(thread_counts, average_runtimes, 3)
    p = np.poly1d(z)
    plt.plot(thread_counts, p(thread_counts), 'r--', alpha=0.8, label='Trend Çizgisi')

    plt.title(f'Thread Sayısına Göre Ortalama Çalışma Süresi\n({ITERATION_COUNT} çalışmanın ortalaması)')
    plt.xlabel('Thread Sayısı')
    plt.ylabel('Ortalama Çalışma Süresi (saniye)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()

    # En iyi performansı gösteren thread sayısı
    best_thread_count = thread_counts[np.argmin(average_runtimes)]
    min_runtime = min(average_runtimes)

    # En iyi noktayı işaretle
    plt.scatter([best_thread_count], [min_runtime], c='red', s=100,
                label=f'En İyi Performans\n({best_thread_count} thread: {min_runtime:.4f}s)')
    plt.legend()

    # İstatistikleri yazdır
    print("\nİstatistikler:")
    print(f"En iyi performans: {best_thread_count} thread ile {min_runtime:.4f} saniye")
    print(f"En kötü performans: {thread_counts[np.argmax(average_runtimes)]} thread ile {max(average_runtimes):.4f} saniye")
    print(f"Ortalama çalışma süresi: {np.mean(average_runtimes):.4f} saniye")

    # Grafiği kaydet
    plt.savefig('thread_runtime_analysis_averaged.png', dpi=300, bbox_inches='tight')
    print("\nGrafik 'thread_runtime_analysis_averaged.png' olarak kaydedildi.")
    plt.close()

if __name__ == "__main__":
    main()

# Created/Modified files during execution:
print("Created files:", ["thread_runtime_analysis_averaged.png"])