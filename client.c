// client.c

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 8080   // 服务器端口
#define SERVER_IP "127.0.0.1"  // 服务器的 IP 地址，替换为实际服务器的 IP
#define BUFFER_SIZE 1024

int main() {
    int client_fd;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];

    // 创建套接字
    if ((client_fd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }

    // 配置服务器地址结构
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    if (inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr) <= 0) {
        perror("Invalid server IP address");
        exit(EXIT_FAILURE);
    }

    // 连接到服务器
    if (connect(client_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("Connection failed");
        close(client_fd);
        exit(EXIT_FAILURE);
    }
    printf("Connected to server %s:%d\n", SERVER_IP, PORT);

    // 发送消息给服务器
    printf("Enter message to send to server: ");
    fgets(buffer, BUFFER_SIZE, stdin);

    // 发送消息
    if (send(client_fd, buffer, strlen(buffer), 0) == -1) {
        perror("Send failed");
        close(client_fd);
        exit(EXIT_FAILURE);
    }
    printf("Message sent to server: %s", buffer);

    // 关闭连接
    close(client_fd);
    return 0;
}
