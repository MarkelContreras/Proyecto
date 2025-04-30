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

    // Errores simulados con crash real
    if (strcmp(buffer, "segfault") == 0) {
        int *ptr = NULL;
        *ptr = 42;  // Provoca segmentation fault
    }

    if (strcmp(buffer, "overflow") == 0) {
        char pequeño[4];
        strcpy(pequeño, "demasiadolargo");  // Buffer overflow
    }

    if (strcmp(buffer, "divzero") == 0) {
        int x = 1 / 0;  // División por cero
        printf("Resultado: %d\n", x);
    }

    if (strcmp(buffer, "abort") == 0) {
        fprintf(stderr, "Abortando...\n");
        abort();  // Lanza SIGABRT
    }

    if (strcmp(buffer, "exit") == 0) {
        exit(77);  // Termina con código arbitrario
    }

    // Casos válidos y código de salida normales
    if (strcmp(buffer, "hello") == 0) {
        printf("Hola, fuzzer\n");
    } else {
        printf("Input recibido: %s\n", buffer);
    }

    return 0;
}
