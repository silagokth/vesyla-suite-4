#include "Drra.hpp"
#include "Util.hpp"
#include <cstdlib>

/*
 * Uncomment the following macro to enable debug mode.
 */
// #define DEBUG

/*
 * Uncomment the following macro to generate human readable output file for
 * debugging. It is mandatory to enable define DATA_TYPE if DEBUG is enabled.
 */
// #define DATA_TYPE int16_t

int main() { return run_simulation(); }

/*
 * Generate the input SRAM image.
 */
void init() {
#define N 16*16
  // Set the seed for random number generator
  srand((unsigned)time(NULL));

  // Generate N random numbers in range [0,100)
  vector<int16_t> v(2 * N);
  for (auto i = 0; i < N+1; i++) {
    v[i] = rand() % 100;
  }

  // Write the random numbers to the input buffer.
  __input_buffer__.write<int16_t>(0, (2 * N) / 16, v);
}

/*
 * Define the reference algorithm model. It will generate the reference output
 * SRAM image. You can use free C++ programs. 
 */
void model_l0() {
#define N 16*16
  // Read the input buffer to A and B.
  vector<int16_t> a = __input_buffer__.read<int16_t>(0, N / 16);
  vector<int16_t> b = __input_buffer__.read<int16_t>(N / 16, N / 16);
  vector<int16_t> c(N+16);
  for(auto i = 0; i < N; i++){
    c[i]=pow(2,(a[i]-b[0]));
    c[N] += c[i];
  }

  // Write A to the output buffer
  __output_buffer__.write<int16_t>(0, N/16+1, c);
}

/*
 * Define the DRR algorithm model. It will generate the DRR output SRAM image by
 * simulate the instruction execution using python simulator.
 */
void model_l1() { simulate_code_segment(0); }