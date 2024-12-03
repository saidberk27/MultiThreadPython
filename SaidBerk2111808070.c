#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>

#define ULTIMATE_MAX_THREAD 32
struct timespec start_time, end_time; // Zaman olcumu degerlerini tutmasi icin veri yapilari
struct thread_args {
    int id;
    int batch_number;
    int total_batch;
}; // Thread fonksiyonuna gonderilecek argumanlari tutan veri yapisi.

unsigned long long int total = 0; 
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

void* thread_function(void* args) {
    struct thread_args* targs = (struct thread_args*)args;
    int thread_id = targs->id;
    int batch_number = targs->batch_number;
    int total_batch = targs->total_batch;

    //Odevde verilmis
    const int N = 10000000;

    // Her batch'in minimum eleman sayýsý.
    int batch_size = N / total_batch;

    // Tam bolunmeyen durumlarda kalani bulmak icin modunu aliyoruz.
    int remainder = N % total_batch;

    // Batch baslangic ve bitis noktalarini hesapliyoruz.
    int batch_interval_start;
    int batch_interval_end;

    if (batch_number <= remainder) { // Tam bolunebilir bir sayiya ulsana kadar bir fazla veriyoruz.
        batch_interval_start = (batch_size + 1) * (batch_number - 1) + 1;
        batch_interval_end = batch_interval_start + batch_size + 1;
    } else {
        // Tam bolunebilir bir sayiya ulastik
        batch_interval_start = (batch_size + 1) * remainder + batch_size * (batch_number - remainder - 1) + 1;
        batch_interval_end = batch_interval_start + batch_size;
    }

    unsigned long long int local_sum = 0; // Her thread'in batch araliginda buldugu toplami tutar.
    int i;
    for(i = batch_interval_start; i < batch_interval_end; i++) {
        local_sum += i; // Butun thread'lerin kendi araliginda buldugu toplamlari toplar
    }

    pthread_mutex_lock(&mutex); // Mutex kilidi acilir.
    total += local_sum; // Global degisken guncellenir.
    pthread_mutex_unlock(&mutex); // Mutex kilidi kapatilir.

    free(args); //Hafizaya iade yapilir
    return NULL;
}

int main() {
    pthread_t threads[ULTIMATE_MAX_THREAD];
    int i;
    // Thread sayisini dinamik tutmak gerekir. Bu dongu 1'den 32'ye kadar arttirir.
    int max_threads;
    for(max_threads = 1; max_threads <= ULTIMATE_MAX_THREAD; max_threads++) {
	clock_gettime(CLOCK_MONOTONIC, &start_time);
        printf("\n---  %d thread ile toplama testi ---\n", max_threads);
        total = 0; // Her test icin toplami sifirla

        for(i = 0; i < max_threads; i++) {
            struct thread_args* args = malloc(sizeof(struct thread_args));
            args->id = i;
            args->batch_number = i + 1;
            args->total_batch = max_threads;

            if (pthread_create(&threads[i], NULL, thread_function, args) != 0) {
                printf("Thread oluþturma hatasý!\n");
                return 1;
            }
        }

        for(i = 0; i < max_threads; i++) {
            pthread_join(threads[i], NULL);
        }

    printf("Thread sayisi %d icin final toplam: %llu\n", max_threads, total);
	clock_gettime(CLOCK_MONOTONIC, &end_time);
	double time_taken = (end_time.tv_sec - start_time.tv_sec) + (end_time.tv_nsec - start_time.tv_nsec) / 1e9;
	printf("\nToplam calisma suresi: %.9f saniye\n", time_taken);  // Nanosaniye hassasiyetinde
    }

    return 0;
}
