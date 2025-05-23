// Copyright (C) 2022 Yu Yang
//
// This file is part of Vesyla.
//
// Vesyla is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Vesyla is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Vesyla.  If not, see <http://www.gnu.org/licenses/>.

#ifndef __DRRA_HPP__
#define __DRRA_HPP__

#include "Array.hpp"
#include "Stream.hpp"
#include "json.hpp"
#include <fstream>
#include <iostream>
#include <regex>

using namespace std;

#define ARCH_IO_DEPTH 65536
#define ARCH_IO_WIDTH 256

typedef Array<ARCH_IO_DEPTH, ARCH_IO_WIDTH> IO;

/*
 * IO interface
 */
IO __input_buffer__;
IO __output_buffer__;

void init();
void model_l0();
void model_l1();

IO file_to_io(string file_) {
  IO io;
  ifstream ifs(file_);
  if (!ifs.is_open()) {
    cout << "Error: Can't open file: " << file_ << endl;
    abort();
  }
  std::string line;
  while (std::getline(ifs, line)) {
    std::smatch sm;
    std::regex e1("\\s*(\\d+)\\s+([01]+)\\s*");
    if (std::regex_match(line.cbegin(), line.cend(), sm, e1)) {
      int addr = stoi(sm[1]);
      string raw_data = sm[2];
      io.write(addr, 1, raw_data);
    }
  }
  return io;
}
void io_to_file(IO io_, string file_) {
  ofstream ofs(file_);
  if (!ofs.is_open()) {
    cout << "Error: Can't open file: " << file_ << endl;
    abort();
  }
  vector<size_t> active_rows = io_.get_active_rows();
  for (size_t idx : active_rows) {
    ofs << idx << " " << io_.read(idx, 1) << endl;
  }
  ofs.close();
}

void load_input_data(string file_) { __input_buffer__ = file_to_io(file_); }
void store_input_data(string file_) { io_to_file(__input_buffer__, file_); }
void load_output_data(string file_) { __output_buffer__ = file_to_io(file_); }
void store_output_data(string file_) { io_to_file(__output_buffer__, file_); }

void bin_to_hex_file(string bin_file_, string hex_file_) {
  ifstream ifs(bin_file_);
  if (!ifs.is_open()) {
    cout << "Error: Can't open file: " << bin_file_ << endl;
    abort();
  }
  ofstream ofs(hex_file_);
  if (!ofs.is_open()) {
    cout << "Error: Can't open file: " << hex_file_ << endl;
    abort();
  }
  std::string line;
  while (std::getline(ifs, line)) {
    std::smatch sm;
    std::regex e1("\\s*(\\d+)\\s+([01]+)\\s*");
    if (std::regex_match(line.cbegin(), line.cend(), sm, e1)) {
      int addr = stoi(sm[1]);
      string raw_data = sm[2];
      string hex_data;
      if (raw_data.size() % 4 != 0) {
        // pad 0s
        raw_data = string(4 - raw_data.size() % 4, '0') + raw_data;
      }
      for (size_t i = 0; i < raw_data.size(); i += 4) {
        unsigned long number = std::bitset<4>(raw_data.substr(i, 4)).to_ulong();
        // convert to hex string
        std::stringstream ss;
        ss << std::hex << number;
        hex_data += ss.str();
      }
      ofs << addr << " " << hex_data << endl;
    }
  }
  ofs.close();
}

template <typename T> void bin_to_num_file(string bin_file_, string num_file_) {
  ifstream ifs(bin_file_);
  if (!ifs.is_open()) {
    cout << "Error: Can't open file: " << bin_file_ << endl;
    abort();
  }
  ofstream ofs(num_file_);
  if (!ofs.is_open()) {
    cout << "Error: Can't open file: " << num_file_ << endl;
    abort();
  }
  std::string line;
  while (std::getline(ifs, line)) {
    std::smatch sm;
    std::regex e1("\\s*(\\d+)\\s+([01]+)\\s*");
    if (std::regex_match(line.cbegin(), line.cend(), sm, e1)) {
      int addr = stoi(sm[1]);
      string raw_data = sm[2];
      // check raw_data size must be multiple of the size of T
      if (raw_data.size() % (sizeof(T) * 8) != 0) {
        cout << "Error: raw_data size is not multiple of " << sizeof(T) * 8
             << endl;
        abort();
      }
      // chop raw_data into chunks
      ofs << addr << " [";
      vector<std::bitset<sizeof(T) * 8>> vec;
      for (size_t i = 0; i < raw_data.size(); i += sizeof(T) * 8) {
        vec.push_back(
            std::bitset<sizeof(T) * 8>(raw_data.substr(i, sizeof(T) * 8)));
      }
      for (size_t i = 0; i < vec.size(); i++) {
        unsigned long num = vec[i].to_ulong();
        T value;
        // use memcpy to fill the value
        memcpy(&value, &num, sizeof(T));
        ofs << value;
        if (i < vec.size() - 1) {
          ofs << ", ";
        }
      }
      ofs << "]" << endl;
    }
  }
  ofs.close();
}

void reset_all() {
  __input_buffer__.reset();
  __output_buffer__.reset();
}

bool verify(string file0_, string file1_) {
  IO io0 = file_to_io(file0_);
  IO io1 = file_to_io(file1_);

  vector<size_t> active_rows_0 = io0.get_active_rows();
  vector<size_t> active_rows_1 = io1.get_active_rows();

  if (active_rows_0.size() != active_rows_1.size()) {
    cout << "Size does not match: " << active_rows_0.size()
         << " != " << active_rows_1.size() << endl;
    return false;
  }

  sort(active_rows_0.begin(), active_rows_0.end());
  sort(active_rows_1.begin(), active_rows_1.end());

  for (size_t idx = 0; idx < active_rows_0.size(); idx++) {
    if (active_rows_0[idx] != active_rows_1[idx]) {
      cout << "Difference address in position " << idx << ": "
           << active_rows_0[idx] << " != " << active_rows_1[idx] << endl;
      return false;
    }

    if (io0.get_slice(active_rows_0[idx]) !=
        io1.get_slice(active_rows_1[idx])) {
      cout << "Difference: address=" << active_rows_0[idx] << endl;
      cout << "In file0: " << io0.get_slice(active_rows_0[idx]) << endl;
      cout << "In file1: " << io1.get_slice(active_rows_1[idx]) << endl;
      return false;
    }
  }
  return true;
}

void set_state_reg(int row, int col, int addr, int value) {
  nlohmann::json j;
  // check if the file exists
  if (ifstream("state_reg.json")) {
    ifstream ifs("state_reg.json");
    ifs >> j;
  }
  string key = to_string(row) + "_" + to_string(col) + "_" + to_string(addr);
  j[key] = value;
  ofstream ofs("state_reg.json");
  ofs << j;
  ofs.close();
}

void simulate_code_segment(int id) {
  string cmd;
  cmd = "vesyla schedule -p ../pasm/" + to_string(id) + ".pasm -c ../pasm/" +
        to_string(id) + ".cstr -o compile";
  assert(system(cmd.c_str()) == 0);
  cmd = "mkdir asm && cp compile/0.asm asm/" + to_string(id) + ".asm";
  assert(system(cmd.c_str()) == 0);
  cmd = "vesyla manas -i asm/" + to_string(id) +
        ".asm -s ../isa.json "
        "-o .";
  assert(system(cmd.c_str()) == 0);
  cmd = "vesyla alimpsim --arch ../arch.json "
        "--instr "
        "instr.bin --isa ../isa.json --input sram_image_in.bin --output "
        "sram_image_m1.bin "
        "--metric metric.json --state_reg state_reg.json";
  assert(system(cmd.c_str()) == 0);
}

int run_simulation() {
  cout << "Initialization ..." << endl;
  init();
  store_input_data("sram_image_in.bin");
#ifdef DEBUG
  bin_to_hex_file("sram_image_in.bin", "sram_image_in.hex");
  bin_to_num_file<DATA_TYPE>("sram_image_in.bin", "sram_image_in.txt");
#endif
  cout << "Run model 0 ..." << endl;
  reset_all();
  load_input_data("sram_image_in.bin");
  model_l0();
  store_output_data("sram_image_m0.bin");
#ifdef DEBUG
  bin_to_hex_file("sram_image_m0.bin", "sram_image_m0.hex");
  bin_to_num_file<DATA_TYPE>("sram_image_m0.bin", "sram_image_m0.txt");
#endif
  cout << "Run model 1 ..." << endl;
  reset_all();
  load_input_data("sram_image_in.bin");
  model_l1();
#ifdef DEBUG
  bin_to_hex_file("sram_image_m1.bin", "sram_image_m1.hex");
  bin_to_num_file<DATA_TYPE>("sram_image_m1.bin", "sram_image_m1.txt");
#endif
  cout << "Verify model 1 against model 0 ..." << endl;
  assert(verify("sram_image_m0.bin", "sram_image_m1.bin"));
  cout << "Success!" << endl;
  return 0;
}

#endif // __DRRA_HPP__
