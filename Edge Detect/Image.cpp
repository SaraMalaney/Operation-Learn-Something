//  Image.cpp
//
#include <cstring>

#ifndef _Image_h
#define _Image_h
#define WIDTH 512
#define HEIGHT 512

#include "Image.h"
#include <cmath>

#endif

using namespace std;
typedef unsigned char unchar;

//Constructor

MImage::MImage(const char* fileName){

    imageData = new unchar* [HEIGHT]; // create new array size: height of image.
    filteredData = new unchar* [HEIGHT];// create new array size: height of image.

    for (int i = 0; i < HEIGHT; i++) {

        imageData[i] = new unchar [WIDTH]; //create matrix.
        filteredData[i] = new unchar [WIDTH]; //create matrix.
    }

    //image I/O
    pInFile = new ifstream;
    pInFile->open(fileName, ios::in | ios::binary); // open fileName and read as binary.
    pInFile->seekg(0, ios::beg); //pos filter at beginning of image file.
    pInFile->read(reinterpret_cast<char*>(imageHeaderData),1078); //read bmp header data into array.

    for(int i=0; i<HEIGHT; i++) {
        pInFile->read(reinterpret_cast<char*>(imageData[i]),WIDTH);//read row into each array entry.
    }

    pInFile->close(); //close stream.

    char m_smoothFilter[3][3] = {
                                 {0,0,0},
                                 {0,0,0},
                                 {0,0,0}
                                };

}

MImage::~MImage(){

    delete pInFile;
    delete pOutFile;

    for(int i=0; i<HEIGHT; i++){
        delete[] imageData[i];
        delete[] filteredData[i];
    }

    delete[] imageData;
    delete[] filteredData;
}

void MImage::write(const char* fileName) {

    smoothFilter();
    pOutFile = new ofstream;
    pOutFile->open(fileName, ios::out | ios::trunc | ios::binary);
    pOutFile->write(reinterpret_cast<char*>(imageHeaderData), 1078); //write header data onto output

    for(int i = 0; i < HEIGHT; i++){

        pOutFile->write(reinterpret_cast<char*>(filteredData[i]),WIDTH); // write new image data.

    }

    pOutFile->close(); //close stream
}

void MImage::smoothFilter(){

    //copy input image into new image
    for(int i= 0; i<HEIGHT; i++) {
        strncpy (reinterpret_cast<char*>(filteredData[i]), 
                 reinterpret_cast<char*>(imageData[i]), 
                 sizeof(reinterpret_cast<char*>(filteredData[i])));
    }

    int sumOfPixels = 0;

    for(int i = 1; i < HEIGHT -1; i++) {

        for(int j = 1; j < WIDTH -1; j++) {

            sumOfPixels = m_smoothFilter[0][0] * imageData[i+1][j-1] + // top left corner
                          m_smoothFilter[0][1] * imageData[i+1][j]   + // top center
                          m_smoothFilter[0][2] * imageData[i+1][j+1] + // top right corner
                          m_smoothFilter[1][0] * imageData[i][j-1]   + // center left
                          m_smoothFilter[1][1] * imageData[i][j]     + // center center
                          m_smoothFilter[1][2] * imageData[i][j+1]   + // center right
                          m_smoothFilter[2][0] * imageData[i-1][j-1] + // bottom left corner
                          m_smoothFilter[2][1] * imageData[i-1][j]   + // bottom center
                          m_smoothFilter[2][2] * imageData[i-1][j+1];  // bottom right corner

            filteredData[i][j] = (sumOfPixels / ( m_smoothFilter[0][0] + m_smoothFilter[0][1] +
                                                  m_smoothFilter[0][2] + m_smoothFilter[1][0] +
                                                  m_smoothFilter[1][1] + m_smoothFilter[1][2] +
                                                  m_smoothFilter[2][0] + m_smoothFilter[2][1] +
                                                 m_smoothFilter[2][2]));
        }
    }

}