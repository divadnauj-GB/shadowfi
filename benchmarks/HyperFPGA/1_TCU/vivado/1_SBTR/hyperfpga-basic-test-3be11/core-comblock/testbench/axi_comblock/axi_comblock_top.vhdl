-- To test the PROC side with a loop in the FPGA side

library IEEE;
use IEEE.std_logic_1164.all;

entity axi_comblock_top is
   port (
      aclk                 : in std_logic;
      aresetn              : in std_logic;
      --
      axil_awaddr          : in std_logic_vector(7 downto 0);
      axil_awvalid         : in std_logic;
      axil_awready         : out std_logic;
      axil_wdata           : in std_logic_vector(31 downto 0);
      axil_wvalid          : in std_logic;
      axil_wready          : out std_logic;
      axil_araddr          : in std_logic_vector(7 downto 0);
      axil_arvalid         : in std_logic;
      axil_arready         : out std_logic;
      axil_rdata           : out std_logic_vector(31 downto 0);
      axil_rvalid          : out std_logic;
      axil_rready          : in std_logic;
      -- Ports of Axi Slave Bus Interface AXIF
      axif_awaddr          : in std_logic_vector(9 downto 0);
      axif_awvalid         : in std_logic;
      axif_awready         : out std_logic;
      axif_wdata           : in std_logic_vector(31 downto 0);
      axif_wvalid          : in std_logic;
      axif_wready          : out std_logic;
      axif_araddr          : in std_logic_vector(9 downto 0);
      axif_arvalid         : in std_logic;
      axif_arready         : out std_logic;
      axif_rdata           : out std_logic_vector(31 downto 0);
      axif_rvalid          : out std_logic;
      axif_rready          : in std_logic
   );
end entity axi_comblock_top;

architecture Structural of axi_comblock_top is
   signal reg0, reg1, reg2, reg3 : std_logic_vector(31 downto 0);
   signal reg4, reg5, reg6, reg7 : std_logic_vector(31 downto 0);
   signal reg8, reg9, regA, regB : std_logic_vector(31 downto 0);
   signal regC, regD, regE, regF : std_logic_vector(31 downto 0);

   signal fifo_empty, fifo_full  : std_logic;
   signal fifo_re,    fifo_we    : std_logic;
   signal fifo_valid             : std_logic;
   signal fifo_datai, fifo_datao : std_logic_vector(15 downto 0);

   signal rst                    : std_logic;
begin

   rst <= not aresetn;

   axi_comblock_inst : entity work.axi_comblock
   generic map (
      REGS_IN_DEPTH  => 16,
      REGS_OUT_DEPTH => 16,
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
      ram_clk_i            => aclk,
      ram_we_i             => '0',
      ram_addr_i           => (others => '0'),
      ram_data_i           => (others => '0'),
      ram_data_o           => open,
      -- fifo
      fifo_clk_i           => aclk,
      fifo_clear_i         => rst,
      -- fifo in
      fifo_we_i            => fifo_we,
      fifo_data_i          => fifo_datai,
      fifo_full_o          => fifo_full,
      fifo_afull_o         => open,
      fifo_overflow_o      => open,
      -- fifo out
      fifo_re_i            => fifo_re,
      fifo_data_o          => fifo_datao,
      fifo_valid_o         => fifo_valid,
      fifo_empty_o         => fifo_empty,
      fifo_aempty_o        => open,
      fifo_underflow_o     => open,
      -- ----------------------------------------------------------------------
      -- PROC side
      -- ----------------------------------------------------------------------
      -- Ports of Axi Slave Bus Interface AXIL
      axil_aclk            =>  aclk,
      axil_aresetn         =>  aresetn,
      axil_awaddr          =>  axil_awaddr,
      axil_awprot          =>  (others => '0'),
      axil_awvalid         =>  axil_awvalid,
      axil_awready         =>  axil_awready,
      axil_wdata           =>  axil_wdata,
      axil_wstrb           =>  (others => '1'),
      axil_wvalid          =>  axil_wvalid,
      axil_wready          =>  axil_wready,
      axil_bresp           =>  open,
      axil_bvalid          =>  open,
      axil_bready          =>  '1',
      axil_araddr          =>  axil_araddr,
      axil_arprot          =>  (others => '0'),
      axil_arvalid         =>  axil_arvalid,
      axil_arready         =>  axil_arready,
      axil_rdata           =>  axil_rdata,
      axil_rresp           =>  open,
      axil_rvalid          =>  axil_rvalid,
      axil_rready          =>  axil_rready,
      -- Ports of Axi Slave Bus Interface AXIF
      axif_aclk            => aclk,
      axif_aresetn         => aresetn,
      axif_awid            => "0",
      axif_awaddr          => axif_awaddr,
      axif_awlen           => "00000000", -- 1
      axif_awsize          => "010",
      axif_awburst         => "01",
      axif_awlock          => '0',
      axif_awcache         => (others => '0'),
      axif_awprot          => (others => '0'),
      axif_awqos           => (others => '0'),
      axif_awregion        => (others => '0'),
      axif_awuser          => (others => '0'),
      axif_awvalid         => axif_awvalid,
      axif_awready         => axif_awready,
      axif_wdata           => axif_wdata,
      axif_wstrb           => (others => '1'),
      axif_wlast           => '1',
      axif_wuser           => (others => '0'),
      axif_wvalid          => axif_wvalid,
      axif_wready          => axif_wready,
      axif_bid             => open,
      axif_bresp           => open,
      axif_buser           => open,
      axif_bvalid          => open,
      axif_bready          => '1',
      axif_arid            => "0",
      axif_araddr          => axif_araddr,
      axif_arlen           => "00000000", -- 1
      axif_arsize          => "010",
      axif_arburst         => "01",
      axif_arlock          => '0',
      axif_arcache         => (others => '0'),
      axif_arprot          => (others => '0'),
      axif_arqos           => (others => '0'),
      axif_arregion        => (others => '0'),
      axif_aruser          => (others => '0'),
      axif_arvalid         => axif_arvalid,
      axif_arready         => axif_arready,
      axif_rid             => open,
      axif_rdata           => axif_rdata,
      axif_rresp           => open,
      axif_rlast           => open,
      axif_ruser           => open,
      axif_rvalid          => axif_rvalid,
      axif_rready          => axif_rready
   );

   fifo_loop_inst : entity work.fifo_loop
   port map (
      clk_i                => aclk,
      data_i               => fifo_datao,
      empty_i              => fifo_empty,
      valid_i              => fifo_valid,
      re_o                 => fifo_re,
      we_o                 => fifo_we,
      data_o               => fifo_datai,
      full_i               => fifo_full
   );

end architecture Structural;
