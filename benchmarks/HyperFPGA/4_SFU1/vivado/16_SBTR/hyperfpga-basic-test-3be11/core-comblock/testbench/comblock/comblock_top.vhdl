-- To test the PROC side with a loop in the FPGA side

library IEEE;
use IEEE.std_logic_1164.all;

entity comblock_top is
   port (
      clk_i         :  in std_logic;
      rst_i         :  in std_logic;
      reg_wr_ena_i  :  in std_logic;
      reg_wr_data_i :  in std_logic_vector(31 downto 0);
      reg_wr_addr_i :  in std_logic_vector(5 downto 0);
      reg_rd_ena_i  :  in std_logic;
      reg_rd_data_o : out std_logic_vector(31 downto 0);
      reg_rd_addr_i :  in std_logic_vector(5 downto 0);
      mem_we_i      :  in std_logic;
      mem_addr_i    :  in std_logic_vector(7 downto 0);
      mem_data_i    :  in std_logic_vector(15 downto 0);
      mem_data_o    : out std_logic_vector(15 downto 0)
   );
end entity comblock_top;

architecture Structural of comblock_top is
   signal reg0, reg1, reg2, reg3 : std_logic_vector(31 downto 0);
   signal reg4, reg5, reg6, reg7 : std_logic_vector(31 downto 0);
   signal reg8, reg9, regA, regB : std_logic_vector(31 downto 0);
   signal regC, regD, regE, regF : std_logic_vector(31 downto 0);

   signal fifo_empty, fifo_full  : std_logic;
   signal fifo_re,    fifo_we    : std_logic;
   signal fifo_valid             : std_logic;
   signal fifo_datai, fifo_datao : std_logic_vector(15 downto 0);
begin

   comblock_inst : entity work.comblock
   generic map (
      DRAM_IO_AWIDTH => 8,
      FIFO_IN_DEPTH  => 256,
      FIFO_OUT_DEPTH => 256
   )
   port map (
      -- ----------------------------------------------------------------------
      -- FPGA side
      -- ----------------------------------------------------------------------
      -- regs
      reg0_i               => reg0,
      reg1_i               => reg1,
      reg2_i               => reg2,
      reg3_i               => reg3,
      reg4_i               => reg4,
      reg5_i               => reg5,
      reg6_i               => reg6,
      reg7_i               => reg7,
      reg8_i               => reg8,
      reg9_i               => reg9,
      reg10_i              => regA,
      reg11_i              => regB,
      reg12_i              => regC,
      reg13_i              => regD,
      reg14_i              => regE,
      reg15_i              => regF,
      reg0_o               => reg0,
      reg1_o               => reg1,
      reg2_o               => reg2,
      reg3_o               => reg3,
      reg4_o               => reg4,
      reg5_o               => reg5,
      reg6_o               => reg6,
      reg7_o               => reg7,
      reg8_o               => reg8,
      reg9_o               => reg9,
      reg10_o              => regA,
      reg11_o              => regB,
      reg12_o              => regC,
      reg13_o              => regD,
      reg14_o              => regE,
      reg15_o              => regF,
      -- true dual ram
      ram_clk_i            => clk_i,
      ram_we_i             => '0',
      ram_addr_i           => (others => '0'),
      ram_data_i           => (others => '0'),
      ram_data_o           => open,
      -- fifo in
      fifo_in_clk_i        => clk_i,
      fifo_in_clear_i      => rst_i,
      fifo_in_we_i         => fifo_we,
      fifo_in_data_i       => fifo_datai,
      fifo_in_full_o       => fifo_full,
      fifo_in_afull_o      => open,
      fifo_in_overflow_o   => open,
      -- fifo out
      fifo_out_clk_i       => clk_i,
      fifo_out_clear_i     => rst_i,
      fifo_out_re_i        => fifo_re,
      fifo_out_data_o      => fifo_datao,
      fifo_out_valid_o     => fifo_valid,
      fifo_out_empty_o     => fifo_empty,
      fifo_out_aempty_o    => open,
      fifo_out_underflow_o => open,
      -- ----------------------------------------------------------------------
      -- PROC side
      -- ----------------------------------------------------------------------
      -- regs
      reg_clk_i            => clk_i,
      reg_wr_ena_i         => reg_wr_ena_i,
      reg_wr_data_i        => reg_wr_data_i,
      reg_wr_addr_i        => reg_wr_addr_i,
      reg_rd_ena_i         => reg_rd_ena_i,
      reg_rd_data_o        => reg_rd_data_o,
      reg_rd_addr_i        => reg_rd_addr_i,
      -- mem
      mem_clk_i            => clk_i,
      mem_we_i             => mem_we_i,
      mem_addr_i           => mem_addr_i,
      mem_data_i           => mem_data_i,
      mem_data_o           => mem_data_o
   );

   fifo_loop_inst : entity work.fifo_loop
   port map (
      clk_i                => clk_i,
      data_i               => fifo_datao,
      empty_i              => fifo_empty,
      valid_i              => fifo_valid,
      re_o                 => fifo_re,
      we_o                 => fifo_we,
      data_o               => fifo_datai,
      full_i               => fifo_full
   );

end architecture Structural;
