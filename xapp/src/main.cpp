#include <iostream>
#include <unistd.h>

int main() {
    std::cout << "Sample xApp starting..." << std::endl;
    
    // Main xApp loop
    while (true) {
        std::cout << "xApp running..." << std::endl;
        sleep(10);
    }
    
    return 0;
}
