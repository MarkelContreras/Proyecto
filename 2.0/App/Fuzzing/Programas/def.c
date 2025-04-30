#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main() {
    char buffer[100];

    // Leer desde stdin
    if (fgets(buffer, sizeof(buffer), stdin) == NULL) {
        return 1;  // Error leyendo input
    }

    // Quitar salto de línea
    buffer[strcspn(buffer, "\n")] = '\0';

    size_t len = strlen(buffer);

    // 🔴 Errores por rango de longitud
    if (len > 0 && len <= 3) {
        fprintf(stderr, "❌ Entrada demasiado corta\n");
        exit(2);  // código 2: demasiado corta
    }

    if (len > 3 && len <= 6) {
        fprintf(stderr, "⚠️ Entrada sospechosa, lanzando abort()\n");
        abort();  // SIGABRT
    }

    if (len > 6 && len <= 10) {
        fprintf(stderr, "💥 División entre 0 simulada\n");
        int x = 1 / 0;  // SIGFPE
    }

    if (len > 10 && len <= 20) {
        fprintf(stderr, "🧨 Accediendo a puntero NULL\n");
        int *ptr = NULL;
        *ptr = 123;  // SIGSEGV
    }

    if (len > 20) {
        fprintf(stderr, "🔥 Buffer overflow forzado\n");
        char pequeño[4];
        strcpy(pequeño, buffer);  // SIGSEGV probable
    }

    // 🔧 Casos explícitos de prueba
    if (strcmp(buffer, "exit") == 0) {
        exit(77);
    }

    if (strcmp(buffer, "hello") == 0) {
        printf("Hola, fuzzer\n");
    } else {
        printf("Input recibido: %s\n", buffer);
    }

    return 0;
}
