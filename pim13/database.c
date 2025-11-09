#include <stdio.h>
#include <string.h>

// 1. Definimos a estrutura EXATAMENTE como o Python vai vê-la.
// É crucial que os tipos e a ordem sejam os mesmos.
typedef struct {
    char nome[100];
    float np1;
    float np2;
    float pim;
    int faltas;
    float media_final;
    char status[20]; // "Aprovado", "Exame", "Reprovado"
} Aluno;

// O 'arquivo_db' onde vamos salvar tudo.
const char* DB_FILE = "alunos.dat";

// 2. Função para salvar um aluno.
// Ela será "exportada" para o Python poder usá-la.
void salvarAluno(Aluno aluno) {
    // Abre o arquivo no modo "ab" (append binary - adicionar binário)
    FILE *f = fopen(DB_FILE, "ab");
    if (f == NULL) {
        // Lidar com erro (idealmente)
        return;
    }
    
    // Escreve a estrutura inteira de uma vez no arquivo
    fwrite(&aluno, sizeof(Aluno), 1, f);
    fclose(f);
}

// 3. Função para carregar todos os alunos.
// Ela recebe um "buffer" (um array) do Python e o preenche.
// Retorna a quantidade de alunos que foram lidos.
int carregarAlunos(Aluno* buffer, int max_alunos) {
    FILE *f = fopen(DB_FILE, "rb"); // "rb" (read binary - ler binário)
    if (f == NULL) {
        return 0; // Arquivo não existe ainda, 0 alunos.
    }

    int count = 0;
    // Lê aluno por aluno do arquivo para o buffer, até o máximo
    while(count < max_alunos && fread(&buffer[count], sizeof(Aluno), 1, f)) {
        count++;
    }
    
    fclose(f);
    return count;
}