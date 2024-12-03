#21118080070 Said Berk
import threading
import time

ULTIMATE_MAX_THREAD = 32
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

    batch_size = N // total_batch #Olusturulacak Batch Sayısı
    remainder = N % total_batch #Tam bolunmeyen sayilar icin kalani bulma

    if batch_number <= remainder: #Tam bolunen bir sayiya ulasilana dek standart batch genisliginin bir fazlasi batch'ler olusturulur
        batch_interval_start = (batch_size + 1) * (batch_number - 1) + 1
        batch_interval_end = batch_interval_start + batch_size + 1
    else:
        #Tam bolunen sayiya ulasilir
        batch_interval_start = (batch_size + 1) * remainder + batch_size * (batch_number - remainder - 1) + 1
        batch_interval_end = batch_interval_start + batch_size

    local_sum = 0 #Batch araligi icin yerel toplam degeri hesaplanir.
    for i in range(batch_interval_start, batch_interval_end):
        local_sum += i #Toplama yapilir

    with mutex: #Global toplam degiskeni kritik bolge
        global total
        total += local_sum #Yerel toplam, global toplam'a eklenir. (Batch merge)

def format_time(nanoseconds):
    seconds = nanoseconds / 1e9
    milliseconds = nanoseconds / 1e6
    microseconds = nanoseconds / 1e3

    return (f"{seconds:.9f} saniye\n"
            f"{milliseconds:.6f} millisaniye\n"
            f"{microseconds:.3f} mikrosaniye\n"
            f"{nanoseconds:.0f} nanosaniye")

def main():
    for max_threads in range(1, ULTIMATE_MAX_THREAD + 1): #Birden fazla thread icin dinamik bir max_thread olusturulur.
        start_time = time.perf_counter_ns()

        print(f"\n---  {max_threads} thread ile toplama testi ---")

        global total
        total = 0

        threads = []
        for i in range(max_threads):
            # ThreadArgs nesnesi oluşturma
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

        end_time = time.perf_counter_ns()
        elapsed_time = end_time - start_time

        print(f"Thread sayisi {max_threads} icin final toplam: {total}")
        print("\nÇalışma süreleri:")
        print(format_time(elapsed_time))

if __name__ == "__main__":
    main()