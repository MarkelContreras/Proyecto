#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main() {
    char buffer[100];
    
    // Leer desde stdin
    if (fgets(buffer, sizeof(buffer), stdin) == NULL) {
        return 1;
    }

    // Quitar salto de línea
    buffer[strcspn(buffer, "\n")] = '\0';

    // Casos que provocan comportamiento especial
    if (strcmp(buffer, "crash") == 0) {
        fprintf(stderr, "¡Crasheando!\n");
        abort(); // Provoca crash
    } else if (strcmp(buffer, "hello") == 0) {
        printf("Hola, fuzzer\n");
    } else {
        printf("Input recibido: %s\n", buffer);
    }

    return 0;
}
