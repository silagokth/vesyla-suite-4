{% for key, value in fingerprint_table | items %}
`define {{key}} {{value}}
`define {{key}}_pkg {{value}}_pkg
{% endfor %}

package fabric_pkg;
    {% for p in parameters %}
    parameter {{p}} = {{parameters[p]}};
    {% endfor %}
endpackage

module fabric
import fabric_pkg::*;
(
    input  logic clk,
    input  logic rst_n,
    input  logic [ROWS-1:0] call,
    output logic [ROWS-1:0] ret,
    output logic [COLS-1:0] io_en_in,
    output logic [COLS-1:0][IO_ADDR_WIDTH-1:0] io_addr_in,
    input  logic [COLS-1:0][IO_DATA_WIDTH-1:0] io_data_in,
    output logic [COLS-1:0] io_en_out,
    output logic [COLS-1:0][IO_ADDR_WIDTH-1:0] io_addr_out,
    output logic [COLS-1:0][IO_DATA_WIDTH-1:0] io_data_out,
    input  logic [ROWS-1:0][INSTR_DATA_WIDTH-1:0] instr_data_in,
    input  logic [ROWS-1:0][INSTR_ADDR_WIDTH-1:0] instr_addr_in,
    input  logic [ROWS-1:0][INSTR_HOPS_WIDTH-1:0] instr_hops_in,
    input  logic [ROWS-1:0] instr_en_in,
    output logic [ROWS-1:0][INSTR_DATA_WIDTH-1:0] instr_data_out,
    output logic [ROWS-1:0][INSTR_ADDR_WIDTH-1:0] instr_addr_out,
    output logic [ROWS-1:0][INSTR_HOPS_WIDTH-1:0] instr_hops_out,
    output logic [ROWS-1:0] instr_en_out
);

    logic [ROWS-1:0][COLS:0] call_net;
    logic [ROWS-1:0][COLS:0] ret_net;
    logic [ROWS-1:0][COLS:0][INSTR_DATA_WIDTH-1:0] instr_data_net;
    logic [ROWS-1:0][COLS:0][INSTR_ADDR_WIDTH-1:0] instr_addr_net;
    logic [ROWS-1:0][COLS:0][INSTR_HOPS_WIDTH-1:0] instr_hops_net;
    logic [ROWS-1:0][COLS:0] instr_en_net;

    always_comb begin
        if (~rst_n) begin
            for (int r=0; r<ROWS; r++) begin
                for (int c=0; c<=COLS; c++) begin
                    call_net[r][c] = 0;
                    ret_net[r][c] = 0;
                    instr_data_net[r][c] = 0;
                    instr_addr_net[r][c] = 0;
                    instr_hops_net[r][c] = 0;
                    instr_en_net[r][c] = 0;
                end
            end
        end
        for (int i=0; i<ROWS; i++) begin
            call_net[i][0] = call[i];
            // ret[i] = ret_net[i][0];
            ret_net[i][COLS] = 1;
            instr_data_net[i][0] = instr_data_in[i];
            instr_addr_net[i][0] = instr_addr_in[i];
            instr_hops_net[i][0] = instr_hops_in[i];
            instr_en_net[i][0] = instr_en_in[i];
            instr_data_out[i] = instr_data_net[i][COLS];
            instr_addr_out[i] = instr_addr_net[i][COLS];
            instr_hops_out[i] = instr_hops_net[i][COLS];
            instr_en_out[i] = instr_en_net[i][COLS];
        end
    end

    for(genvar i=0; i<ROWS; i++) begin
        assign ret[i] = ret_net[i][0];
    end

    {% for cell in cells %}
    {%- set r=cell.coordinates.row -%}
    {%- set c=cell.coordinates.col -%}
    `{{cell.cell.name}} cell_{{r}}_{{c}}_inst (
        .clk(clk),
        .rst_n(rst_n),
        .call_in(call_net[{{r}}][{{c}}]),
        .call_out(call_net[{{r}}][{{c + 1}}]),
        .ret_in(ret_net[{{r}}][{{c + 1}}]),
        .ret_out(ret_net[{{r}}][{{c}}]),
        .io_en_in(io_en_in[{{c}}]),
        .io_addr_in(io_addr_in[{{c}}]),
        .io_data_in(io_data_in[{{c}}]),
        .io_en_out(io_en_out[{{c}}]),
        .io_addr_out(io_addr_out[{{c}}]),
        .io_data_out(io_data_out[{{c}}]),
        .instr_data_in(instr_data_net[{{r}}][{{c}}]),
        .instr_addr_in(instr_addr_net[{{r}}][{{c}}]),
        .instr_hops_in(instr_hops_net[{{r}}][{{c}}]),
        .instr_en_in(instr_en_net[{{r}}][{{c}}]),
        .instr_data_out(instr_data_net[{{r}}][{{c + 1}}]),
        .instr_addr_out(instr_addr_net[{{r}}][{{c + 1}}]),
        .instr_hops_out(instr_hops_net[{{r}}][{{c + 1}}]),
        .instr_en_out(instr_en_net[{{r}}][{{c + 1}}])
    );
    {% endfor %}
endmodule
