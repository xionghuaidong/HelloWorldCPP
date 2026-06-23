#include <iostream>
#include <thread>
#include <tchar.h>
#include <Windows.h>
#include <CommCtrl.h>

int _tmain(void)
{
    // Enable visual styles.
    InitCommonControls();

    std::thread t([] { std::cout << "thread\n"; });
    std::cout << "main\n";
    t.join();

    //MessageBox(NULL, TEXT("Hello, World! [C++]"), TEXT("hello"), MB_ICONINFORMATION);
    return 0;
}
