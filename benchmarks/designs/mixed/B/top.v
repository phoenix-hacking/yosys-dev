// Small ASIC bring-up fixture, not a capacity or PPA benchmark.
module mixed_top (
    input wire clk, input wire rst,
    input wire [7:0] a, b, input wire select,
    output reg [15:0] product, output reg [8:0] result,
    output reg [7:0] count
);
    wire [15:0] multiply_result = a * b;
    wire [8:0] selected_result = select ? ({1'b0,a} + {1'b0,b}) : {1'b0,b};
    always @(posedge clk) begin
        if (rst) begin
            product <= 0;
            result <= 0;
            count <= 0;
        end else begin
            product <= multiply_result;
            result <= selected_result;
            count <= count + 1'b1;
        end
    end
endmodule
