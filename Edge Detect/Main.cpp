//
//  Main.cpp
//

#include <cstring>
#include <iostream>
#include "Image.cpp"
#include <fstream>

using namespace std;

int main() {

    MImage img("lena512.bmp");
    img.write("output.bmp");
    return 0;

}