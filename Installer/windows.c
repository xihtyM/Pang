#include <stdio.h>
#include <direct.h>
#include <urlmon.h>
#include <locale.h>

void download(const char *url, const char *file) {
    HRESULT hr;

    hr = URLDownloadToFileA(
        NULL,
        url,
        file,
        BINDF_GETNEWESTVERSION,
        NULL);


    if (hr != S_OK) {
        printf(hr == E_OUTOFMEMORY ?
              "Error: Not enough memory to download file.\n"
            : "Error: URL is not valid, please make sure you are using the latest installer.\n");
        exit(1);
    }
}

#define GIT_LINK "https://raw.githubusercontent.com/xihtyM/Pang/main/"
#define pang_download(path, file) download(GIT_LINK file, path file)

void pang_mkdir(const char *path) {
    if (_mkdir(path) != 0) {
        printf("Error: Failed to create directory. Make sure you are running as an administrator.\n");
        exit(1);
    }
}

char *getline(char *str, unsigned int line) {
    char *split;
    int start;
    int length;

    for (start = 0; str[start] != 0 && line > 0; start++) {
        if (str[start] == '\n') {
            line--;
        }
    }

    if (str[start] == 0) {
        return ""; // Return blank string because there are not enough lines.
    }

    for (length = 0; str[start + length] != '\n' && str[start + length] != 0; length++);

    split = malloc(length + 1);

    for (int index = 0; index < length; index++) {
        split[index] = str[index + start];
    }

    split[length] = 0;

    return split;
}

void download_pangfiles(char *files) {
    int lines = 0;
    char *filename;

    while ((filename = getline(files, lines++)) != "") {
        int url_length = strlen(GIT_LINK) + strlen(filename);
        char *url = malloc(url_length + 1);
        
        strcpy(url, GIT_LINK);
        strcat(url, filename);
        url[url_length] = 0;

        int file_length = strlen(GIT_LINK) + strlen(filename);
        char *file = malloc(file_length + 1);
        
        strcpy(file, "Pang\\");
        strcat(file, filename);
        file[file_length] = 0;

        printf("Downloading %s from %s\n", filename, url);

        download(url, file);

        free(filename);
        free(file);
        free(url);
    }
}

int main(void) {
    setlocale(LC_ALL, ".utf-8");
    _chdir(getenv("ProgramFiles"));

    pang_mkdir("Pang");
    pang_download("Pang\\", "files");

    FILE *files_ptr = fopen("Pang\\files", "r");

    if (!files_ptr) {
        printf("Error: Could not download files.\n");
        exit(1);
    }

    fseek(files_ptr, 0, SEEK_END);
    long fsize = ftell(files_ptr);
    fseek(files_ptr, 0, SEEK_SET);

    char *files = malloc(fsize + 1);
    fread(files, fsize, 1, files_ptr);
    fclose(files_ptr);

    files[fsize] = 0;

    download_pangfiles(files);
    free(files);
    remove("Pang\\files");

    return 0;
}
