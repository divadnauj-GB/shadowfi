--
-- ComBlock (AXI4)
--
-- Author(s):
-- * Rodrigo A. Melo
--
-- Copyright (c) 2018-2019 Authors, INTI (MNT) and ICTP (MLAB)
-- Distributed under the BSD 3-Clause License
--
-- Description: A simple and portable COMmunication BLOCK with well know
-- interfaces in the FPGA side. AXI4 version.
--

library IEEE;
use IEEE.std_logic_1164.all;

entity axi_comblock is
   generic (
      REGS_IN_ENA          : boolean  := true;
      REGS_IN_DWIDTH       : positive := 32;
      REGS_IN_DEPTH        : positive := 4;
      --
      REGS_OUT_ENA         : boolean  := true;
      REGS_OUT_DWIDTH      : positive := 32;
      REGS_OUT_DEPTH       : positive := 4;
      --
      DRAM_IO_ENA          : boolean  := true;
      DRAM_IO_DWIDTH       : positive := 16;
      DRAM_IO_AWIDTH       : positive := 16;
      DRAM_IO_DEPTH        : natural  := 0;
      --
      FIFO_IN_ENA          : boolean  := true;
      FIFO_IN_DWIDTH       : positive := 16;
      FIFO_IN_DEPTH        : positive := 1024;
      FIFO_IN_AFOFFSET     : natural  := 1;
      FIFO_IN_AEOFFSET     : natural  := 1;
      --
      FIFO_OUT_ENA         : boolean  := false;
      FIFO_OUT_DWIDTH      : positive := 16;
      FIFO_OUT_DEPTH       : positive := 1024;
      FIFO_OUT_AFOFFSET    : natural  := 1;
      FIFO_OUT_AEOFFSET    : natural  := 1;
      -- AXI support parameters (hidden)
      -- Parameters of Axi Slave Bus Interface AXIF
      C_AXIF_ID_WIDTH      : natural  := 1;
      C_AXIF_AWUSER_WIDTH  : natural  := 0;
      C_AXIF_ARUSER_WIDTH  : natural  := 0;
      C_AXIF_WUSER_WIDTH   : natural  := 0;
      C_AXIF_RUSER_WIDTH   : natural  := 0;
      C_AXIF_BUSER_WIDTH   : natural  := 0
   );
   port (
      -- ----------------------------------------------------------------------
      -- FPGA side
      -- ----------------------------------------------------------------------
      -- regs
      reg0_i               :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg1_i               :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg2_i               :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg3_i               :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg4_i               :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg5_i               :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg6_i               :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg7_i               :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg8_i               :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg9_i               :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg10_i              :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg11_i              :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg12_i              :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg13_i              :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg14_i              :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg15_i              :  in std_logic_vector(REGS_IN_DWIDTH-1 downto 0):=(others => '0');
      reg0_o               : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      reg1_o               : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      reg2_o               : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      reg3_o               : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      reg4_o               : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      reg5_o               : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      reg6_o               : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      reg7_o               : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      reg8_o               : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      reg9_o               : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      reg10_o              : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      reg11_o              : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      reg12_o              : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      reg13_o              : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      reg14_o              : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      reg15_o              : out std_logic_vector(REGS_OUT_DWIDTH-1 downto 0);
      -- true dual ram
      ram_clk_i            :  in std_logic:='0';
      ram_we_i             :  in std_logic:='0';
      ram_addr_i           :  in std_logic_vector(DRAM_IO_AWIDTH-1 downto 0):=(others => '0');
      ram_data_i           :  in std_logic_vector(DRAM_IO_DWIDTH-1 downto 0):=(others => '0');
      ram_data_o           : out std_logic_vector(DRAM_IO_DWIDTH-1 downto 0);
      -- fifo
      fifo_clk_i           :  in std_logic:='0';
      fifo_clear_i         :  in std_logic:='0';
      -- fifo in
      fifo_we_i            :  in std_logic:='0';
      fifo_data_i          :  in std_logic_vector(FIFO_IN_DWIDTH-1 downto 0):=(others => '0');
      fifo_full_o          : out std_logic;
      fifo_afull_o         : out std_logic;
      fifo_overflow_o      : out std_logic;
      -- fifo out
      fifo_re_i            :  in std_logic:='0';
      fifo_data_o          : out std_logic_vector(FIFO_OUT_DWIDTH-1 downto 0);
      fifo_valid_o         : out std_logic;
      fifo_empty_o         : out std_logic;
      fifo_aempty_o        : out std_logic;
      fifo_underflow_o     : out std_logic;
      -- ----------------------------------------------------------------------
      -- PROC side
      -- ----------------------------------------------------------------------
      -- Ports of Axi Slave Bus Interface AXIL
      axil_aclk            : in std_logic;
      axil_aresetn         : in std_logic;
      axil_awaddr          : in std_logic_vector(7 downto 0);
      axil_awprot          : in std_logic_vector(2 downto 0);
      axil_awvalid         : in std_logic;
      axil_awready         : out std_logic;
      axil_wdata           : in std_logic_vector(31 downto 0);
      axil_wstrb           : in std_logic_vector(3 downto 0);
      axil_wvalid          : in std_logic;
      axil_wready          : out std_logic;
      axil_bresp           : out std_logic_vector(1 downto 0);
      axil_bvalid          : out std_logic;
      axil_bready          : in std_logic;
      axil_araddr          : in std_logic_vector(7 downto 0);
      axil_arprot          : in std_logic_vector(2 downto 0);
      axil_arvalid         : in std_logic;
      axil_arready         : out std_logic;
      axil_rdata           : out std_logic_vector(31 downto 0);
      axil_rresp           : out std_logic_vector(1 downto 0);
      axil_rvalid          : out std_logic;
      axil_rready          : in std_logic;
      -- Ports of Axi Slave Bus Interface AXIF
      axif_aclk            : in std_logic;
      axif_aresetn         : in std_logic;
      axif_awid            : in std_logic_vector(C_AXIF_ID_WIDTH-1 downto 0);
      axif_awaddr          : in std_logic_vector(DRAM_IO_AWIDTH+2-1 downto 0);
      axif_awlen           : in std_logic_vector(7 downto 0);
      axif_awsize          : in std_logic_vector(2 downto 0);
      axif_awburst         : in std_logic_vector(1 downto 0);
      axif_awlock          : in std_logic;
      axif_awcache         : in std_logic_vector(3 downto 0);
      axif_awprot          : in std_logic_vector(2 downto 0);
      axif_awqos           : in std_logic_vector(3 downto 0);
      axif_awregion        : in std_logic_vector(3 downto 0);
      axif_awuser          : in std_logic_vector(C_AXIF_AWUSER_WIDTH-1 downto 0);
      axif_awvalid         : in std_logic;
      axif_awready         : out std_logic;
      axif_wdata           : in std_logic_vector(31 downto 0);
      axif_wstrb           : in std_logic_vector(3 downto 0);
      axif_wlast           : in std_logic;
      axif_wuser           : in std_logic_vector(C_AXIF_WUSER_WIDTH-1 downto 0);
      axif_wvalid          : in std_logic;
      axif_wready          : out std_logic;
      axif_bid             : out std_logic_vector(C_AXIF_ID_WIDTH-1 downto 0);
      axif_bresp           : out std_logic_vector(1 downto 0);
      axif_buser           : out std_logic_vector(C_AXIF_BUSER_WIDTH-1 downto 0);
      axif_bvalid          : out std_logic;
      axif_bready          : in std_logic;
      axif_arid            : in std_logic_vector(C_AXIF_ID_WIDTH-1 downto 0);
      axif_araddr          : in std_logic_vector(DRAM_IO_AWIDTH+2-1 downto 0);
      axif_arlen           : in std_logic_vector(7 downto 0);
      axif_arsize          : in std_logic_vector(2 downto 0);
      axif_arburst         : in std_logic_vector(1 downto 0);
      axif_arlock          : in std_logic;
      axif_arcache         : in std_logic_vector(3 downto 0);
      axif_arprot          : in std_logic_vector(2 downto 0);
      axif_arqos           : in std_logic_vector(3 downto 0);
      axif_arregion        : in std_logic_vector(3 downto 0);
      axif_aruser          : in std_logic_vector(C_AXIF_ARUSER_WIDTH-1 downto 0);
      axif_arvalid         : in std_logic;
      axif_arready         : out std_logic;
      axif_rid             : out std_logic_vector(C_AXIF_ID_WIDTH-1 downto 0);
      axif_rdata           : out std_logic_vector(31 downto 0);
      axif_rresp           : out std_logic_vector(1 downto 0);
      axif_rlast           : out std_logic;
      axif_ruser           : out std_logic_vector(C_AXIF_RUSER_WIDTH-1 downto 0);
      axif_rvalid          : out std_logic;
      axif_rready          : in std_logic
   );
end entity axi_comblock;

architecture Structural of axi_comblock is

   signal reg_wr_adr, reg_rd_adr : std_logic_vector(7 downto 0);
   signal reg_wr_dat, reg_rd_dat : std_logic_vector(31 downto 0);
   signal reg_wr_ena, reg_rd_ena : std_logic;

   signal mem_wr_adr, mem_rd_adr : std_logic_vector(DRAM_IO_AWIDTH+2-1 downto 0);
   signal mem_wr_dat, mem_rd_dat : std_logic_vector(31 downto 0):=(others => '0');
   signal mem_wr_ena             : std_logic;
   signal mem_adr                : std_logic_vector(DRAM_IO_AWIDTH+2-1 downto 0);

begin

   AXIL_inst : entity work.axil
   generic map (
      C_S_AXI_DATA_WIDTH   => 32,
      C_S_AXI_ADDR_WIDTH   => 8
   )
   port map (
      wr_adr_o             => reg_wr_adr,
      wr_dat_o             => reg_wr_dat,
      wr_val_o             => reg_wr_ena,
      rd_adr_o             => reg_rd_adr,
      rd_dat_i             => reg_rd_dat,
      rd_val_o             => reg_rd_ena,
      --
      S_AXI_ACLK           => axil_aclk,
      S_AXI_ARESETN        => axil_aresetn,
      S_AXI_AWADDR         => axil_awaddr,
      S_AXI_AWPROT         => axil_awprot,
      S_AXI_AWVALID        => axil_awvalid,
      S_AXI_AWREADY        => axil_awready,
      S_AXI_WDATA          => axil_wdata,
      S_AXI_WSTRB          => axil_wstrb,
      S_AXI_WVALID         => axil_wvalid,
      S_AXI_WREADY         => axil_wready,
      S_AXI_BRESP          => axil_bresp,
      S_AXI_BVALID         => axil_bvalid,
      S_AXI_BREADY         => axil_bready,
      S_AXI_ARADDR         => axil_araddr,
      S_AXI_ARPROT         => axil_arprot,
      S_AXI_ARVALID        => axil_arvalid,
      S_AXI_ARREADY        => axil_arready,
      S_AXI_RDATA          => axil_rdata,
      S_AXI_RRESP          => axil_rresp,
      S_AXI_RVALID         => axil_rvalid,
      S_AXI_RREADY         => axil_rready
   );

   AXIF_inst : entity work.axif
   generic map (
      C_S_AXI_ID_WIDTH     => C_AXIF_ID_WIDTH,
      C_S_AXI_DATA_WIDTH   => 32,
      C_S_AXI_ADDR_WIDTH   => DRAM_IO_AWIDTH+2,
      C_S_AXI_AWUSER_WIDTH => C_AXIF_AWUSER_WIDTH,
      C_S_AXI_ARUSER_WIDTH => C_AXIF_ARUSER_WIDTH,
      C_S_AXI_WUSER_WIDTH  => C_AXIF_WUSER_WIDTH,
      C_S_AXI_RUSER_WIDTH  => C_AXIF_RUSER_WIDTH,
      C_S_AXI_BUSER_WIDTH  => C_AXIF_BUSER_WIDTH
   )
   port map (
      wr_adr_o             => mem_wr_adr,
      wr_dat_o             => mem_wr_dat,
      wr_val_o             => mem_wr_ena,
      rd_adr_o             => mem_rd_adr,
      rd_dat_i             => mem_rd_dat,
      rd_val_o             => open,
      --
      S_AXI_ACLK           => axif_aclk,
      S_AXI_ARESETN        => axif_aresetn,
      S_AXI_AWID           => axif_awid,
      S_AXI_AWADDR         => axif_awaddr,
      S_AXI_AWLEN          => axif_awlen,
      S_AXI_AWSIZE         => axif_awsize,
      S_AXI_AWBURST        => axif_awburst,
      S_AXI_AWLOCK         => axif_awlock,
      S_AXI_AWCACHE        => axif_awcache,
      S_AXI_AWPROT         => axif_awprot,
      S_AXI_AWQOS          => axif_awqos,
      S_AXI_AWREGION       => axif_awregion,
      S_AXI_AWUSER         => axif_awuser,
      S_AXI_AWVALID        => axif_awvalid,
      S_AXI_AWREADY        => axif_awready,
      S_AXI_WDATA          => axif_wdata,
      S_AXI_WSTRB          => axif_wstrb,
      S_AXI_WLAST          => axif_wlast,
      S_AXI_WUSER          => axif_wuser,
      S_AXI_WVALID         => axif_wvalid,
      S_AXI_WREADY         => axif_wready,
      S_AXI_BID            => axif_bid,
      S_AXI_BRESP          => axif_bresp,
      S_AXI_BUSER          => axif_buser,
      S_AXI_BVALID         => axif_bvalid,
      S_AXI_BREADY         => axif_bready,
      S_AXI_ARID           => axif_arid,
      S_AXI_ARADDR         => axif_araddr,
      S_AXI_ARLEN          => axif_arlen,
      S_AXI_ARSIZE         => axif_arsize,
      S_AXI_ARBURST        => axif_arburst,
      S_AXI_ARLOCK         => axif_arlock,
      S_AXI_ARCACHE        => axif_arcache,
      S_AXI_ARPROT         => axif_arprot,
      S_AXI_ARQOS          => axif_arqos,
      S_AXI_ARREGION       => axif_arregion,
      S_AXI_ARUSER         => axif_aruser,
      S_AXI_ARVALID        => axif_arvalid,
      S_AXI_ARREADY        => axif_arready,
      S_AXI_RID            => axif_rid,
      S_AXI_RDATA          => axif_rdata,
      S_AXI_RRESP          => axif_rresp,
      S_AXI_RLAST          => axif_rlast,
      S_AXI_RUSER          => axif_ruser,
      S_AXI_RVALID         => axif_rvalid,
      S_AXI_RREADY         => axif_rready
   );

   comblock_i: entity work.comblock
    generic map (
      REGS_IN_ENA          => REGS_IN_ENA,
      REGS_IN_DWIDTH       => REGS_IN_DWIDTH,
      REGS_IN_DEPTH        => REGS_IN_DEPTH,
      --
      REGS_OUT_ENA         => REGS_OUT_ENA,
      REGS_OUT_DWIDTH      => REGS_OUT_DWIDTH,
      REGS_OUT_DEPTH       => REGS_OUT_DEPTH,
      --
      DRAM_IO_ENA          => DRAM_IO_ENA,
      DRAM_IO_DWIDTH       => DRAM_IO_DWIDTH,
      DRAM_IO_AWIDTH       => DRAM_IO_AWIDTH,
      DRAM_IO_DEPTH        => DRAM_IO_DEPTH,
      --
      FIFO_IN_ENA          => FIFO_IN_ENA,
      FIFO_IN_DWIDTH       => FIFO_IN_DWIDTH,
      FIFO_IN_DEPTH        => FIFO_IN_DEPTH,
      FIFO_IN_AFOFFSET     => FIFO_IN_AFOFFSET,
      FIFO_IN_AEOFFSET     => FIFO_IN_AEOFFSET,
      --
      FIFO_OUT_ENA         => FIFO_OUT_ENA,
      FIFO_OUT_DWIDTH      => FIFO_OUT_DWIDTH,
      FIFO_OUT_DEPTH       => FIFO_OUT_DEPTH,
      FIFO_OUT_AFOFFSET    => FIFO_OUT_AFOFFSET,
      FIFO_OUT_AEOFFSET    => FIFO_OUT_AEOFFSET
   )
   port map (
      -- ----------------------------------------------------------------------
      -- FPGA side
      -- ----------------------------------------------------------------------
      -- regs
      reg0_i               => reg0_i,
      reg1_i               => reg1_i,
      reg2_i               => reg2_i,
      reg3_i               => reg3_i,
      reg4_i               => reg4_i,
      reg5_i               => reg5_i,
      reg6_i               => reg6_i,
      reg7_i               => reg7_i,
      reg8_i               => reg8_i,
      reg9_i               => reg9_i,
      reg10_i              => reg10_i,
      reg11_i              => reg11_i,
      reg12_i              => reg12_i,
      reg13_i              => reg13_i,
      reg14_i              => reg14_i,
      reg15_i              => reg15_i,
      reg0_o               => reg0_o,
      reg1_o               => reg1_o,
      reg2_o               => reg2_o,
      reg3_o               => reg3_o,
      reg4_o               => reg4_o,
      reg5_o               => reg5_o,
      reg6_o               => reg6_o,
      reg7_o               => reg7_o,
      reg8_o               => reg8_o,
      reg9_o               => reg9_o,
      reg10_o              => reg10_o,
      reg11_o              => reg11_o,
      reg12_o              => reg12_o,
      reg13_o              => reg13_o,
      reg14_o              => reg14_o,
      reg15_o              => reg15_o,
      -- true dual ram
      ram_clk_i            => ram_clk_i,
      ram_we_i             => ram_we_i,
      ram_addr_i           => ram_addr_i,
      ram_data_i           => ram_data_i,
      ram_data_o           => ram_data_o,
      -- fifo in
      fifo_in_clk_i        => fifo_clk_i,
      fifo_in_clear_i      => fifo_clear_i,
      fifo_in_we_i         => fifo_we_i,
      fifo_in_data_i       => fifo_data_i,
      fifo_in_full_o       => fifo_full_o,
      fifo_in_afull_o      => fifo_afull_o,
      fifo_in_overflow_o   => fifo_overflow_o,
      -- fifo out
      fifo_out_clk_i       => fifo_clk_i,
      fifo_out_clear_i     => fifo_clear_i,
      fifo_out_re_i        => fifo_re_i,
      fifo_out_data_o      => fifo_data_o,
      fifo_out_valid_o     => fifo_valid_o,
      fifo_out_empty_o     => fifo_empty_o,
      fifo_out_aempty_o    => fifo_aempty_o, 
      fifo_out_underflow_o => fifo_underflow_o,
      -- ----------------------------------------------------------------------
      -- PROC side
      -- ----------------------------------------------------------------------
      -- regs
      reg_clk_i            => axil_aclk,
      reg_wr_ena_i         => reg_wr_ena,
      reg_wr_data_i        => reg_wr_dat,
      reg_wr_addr_i        => reg_wr_adr(7 downto 2),
      reg_rd_ena_i         => reg_rd_ena,
      reg_rd_data_o        => reg_rd_dat,
      reg_rd_addr_i        => reg_rd_adr(7 downto 2),
      -- mem
      mem_clk_i            => axif_aclk,
      mem_we_i             => mem_wr_ena,
      mem_addr_i           => mem_adr(DRAM_IO_AWIDTH+2-1 downto 2),
      mem_data_i           => mem_wr_dat(DRAM_IO_DWIDTH-1 downto 0),
      mem_data_o           => mem_rd_dat(DRAM_IO_DWIDTH-1 downto 0)
   );

   mem_adr <= mem_wr_adr when mem_wr_ena = '1' else mem_rd_adr;

end architecture Structural;
