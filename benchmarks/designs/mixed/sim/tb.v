`timescale 1ns/1ps
module mixed_tb;
    reg clk = 0, rst = 1, select = 1;
    reg [7:0] a = 255, b = 255;
    wire [15:0] product;
    wire [8:0] result;
    wire [7:0] count;
    mixed_top dut(clk, rst, a, b, select, product, result, count);
    always #5 clk = ~clk;
    initial begin
        #6;
        if ({product, result, count} !== 0) $fatal(1, "Reset failed");
        rst = 0;
        #10;
        if (product !== 16'd65025 || result !== 9'd510 || count !== 8'd1)
            $fatal(1, "Datapath failed");
        select = 0;
        #10;
        if (result !== 9'd255 || count !== 8'd2) $fatal(1, "Select/count failed");
        $display("ASIC_FLOW_IP_PASS");
        $finish;
    end
endmodule
