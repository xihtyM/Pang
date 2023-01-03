#include <stdio.h>
#include <stdbool.h>
#include <direct.h>
#include <urlmon.h>
#include <locale.h>
#include <sys/stat.h>

bool SetPermanentEnvironmentVariable(LPCSTR value, LPCSTR data) {
    HKEY hKey;
    LPCSTR keyPath = "System\\CurrentControlSet\\Control\\Session Manager\\Environment";
    LSTATUS lOpenStatus = RegOpenKeyExA(HKEY_LOCAL_MACHINE, keyPath, 0, KEY_ALL_ACCESS, &hKey);

    if (lOpenStatus == ERROR_SUCCESS) {
        LSTATUS lSetStatus = RegSetValueExA(hKey, value, 0, REG_SZ,(LPBYTE)data, strlen(data) + 1);
        RegCloseKey(hKey);

        if (lSetStatus == ERROR_SUCCESS) {
            SendMessageTimeoutA(HWND_BROADCAST, WM_SETTINGCHANGE, 0, (LPARAM)"Environment", SMTO_BLOCK, 100, NULL);
            return true;
        }
    }

    return false;
}

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
    struct stat path_stat;
    stat(path, &path_stat);

    if ((path_stat.st_mode & S_IFMT) == S_IFDIR) {
        char *command = malloc((strlen(path) * 2) + 36);

        strcpy(command, "del /f /s /q ");
        strcat(command, path);
        strcat(command, " 1>nul && rmdir /s /q ");
        strcat(command, path);

        system(command);
        free(command);
    }

    if (_mkdir(path) != 0) {
        printf("Error: Failed to create directory. Make sure you are running as an administrator.\nError: %s", strerror(errno));
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

    while (strlen(filename = getline(files, lines++)) > 0) {
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

    _chdir(getenv("AppData"));

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

    char *pang_path = malloc(strlen(getenv("AppData")) + strlen("\\Pang") + 1);
    strcpy(pang_path, getenv("AppData"));
    strcat(pang_path, "\\Pang");

    SetPermanentEnvironmentVariable("pang", pang_path);
    free(pang_path);

    char *bat_path = malloc(strlen(getenv("windir")) + 19);
    strcpy(bat_path, getenv("windir"));
    strcat(bat_path, "\\System32\\pang.bat");

    FILE *bat = fopen(bat_path, "w");
    
    if (bat == NULL) {
        printf("Error: Failed to create batch file. %s\n", strerror(errno));
        exit(1);
    }
    
    fwrite("@echo off\npython3 \"%pang%\\pang.py\" %*", strlen("@echo off\npython3 \"%pang%\\pang.py\" %*"), 1, bat);
    fclose(bat);
    free(bat_path);

    return 0;
}
