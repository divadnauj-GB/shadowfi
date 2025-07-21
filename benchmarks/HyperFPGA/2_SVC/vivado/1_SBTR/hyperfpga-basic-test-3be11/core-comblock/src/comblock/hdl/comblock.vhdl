--
-- ComBlock
--
-- Author(s):
-- * Rodrigo A. Melo
--
-- Copyright (c) 2018-2019 Authors, INTI (MNT) and ICTP (MLAB)
-- Distributed under the BSD 3-Clause License
--
-- Description: A simple and portable COMmunication BLOCK with well know
-- interfaces in the FPGA side
--

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity ComBlock is
   generic (
      REGS_IN_ENA          : boolean  := true;
      REGS_IN_DWIDTH       : positive := 32;
      REGS_IN_DEPTH        : positive := 16;
      --
      REGS_OUT_ENA         : boolean  := true;
      REGS_OUT_DWIDTH      : positive := 32;
      REGS_OUT_DEPTH       : positive := 16;
      --
      DRAM_IO_ENA          : boolean  := true;
      DRAM_IO_DWIDTH       : positive := 16;
      DRAM_IO_AWIDTH       : positive := 16;
      DRAM_IO_DEPTH        : natural  := 0;
      --
      FIFO_IN_ENA          : boolean  := true;
      FIFO_IN_DWIDTH       : positive := 16;
      FIFO_IN_DEPTH        : positive := 1024;
      FIFO_IN_AFOFFSET     : positive := 1;
      FIFO_IN_AEOFFSET     : positive := 1;
      --
      FIFO_OUT_ENA         : boolean  := true;
      FIFO_OUT_DWIDTH      : positive := 16;
      FIFO_OUT_DEPTH       : positive := 1024;
      FIFO_OUT_AFOFFSET    : positive := 1;
      FIFO_OUT_AEOFFSET    : positive := 1
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
      -- fifo in
      fifo_in_clk_i        :  in std_logic:='0';
      fifo_in_clear_i      :  in std_logic:='0';
      fifo_in_we_i         :  in std_logic:='0';
      fifo_in_data_i       :  in std_logic_vector(FIFO_IN_DWIDTH-1 downto 0):=(others => '0');
      fifo_in_full_o       : out std_logic;
      fifo_in_afull_o      : out std_logic;
      fifo_in_overflow_o   : out std_logic;
      -- fifo out
      fifo_out_clk_i       :  in std_logic:='0';
      fifo_out_clear_i     :  in std_logic:='0';
      fifo_out_re_i        :  in std_logic:='0';
      fifo_out_data_o      : out std_logic_vector(FIFO_OUT_DWIDTH-1 downto 0);
      fifo_out_valid_o     : out std_logic;
      fifo_out_empty_o     : out std_logic;
      fifo_out_aempty_o    : out std_logic;
      fifo_out_underflow_o : out std_logic;
      -- ----------------------------------------------------------------------
      -- PROC side
      -- ----------------------------------------------------------------------
      -- regs
      reg_clk_i            :  in std_logic;
      reg_wr_ena_i         :  in std_logic;
      reg_wr_data_i        :  in std_logic_vector(31 downto 0);
      reg_wr_addr_i        :  in std_logic_vector(5 downto 0);
      reg_rd_ena_i         :  in std_logic;
      reg_rd_data_o        : out std_logic_vector(31 downto 0);
      reg_rd_addr_i        :  in std_logic_vector(5 downto 0);
      -- mem
      mem_clk_i            :  in std_logic;
      mem_we_i             :  in std_logic;
      mem_addr_i           :  in std_logic_vector(DRAM_IO_AWIDTH-1 downto 0);
      mem_data_i           :  in std_logic_vector(DRAM_IO_DWIDTH-1 downto 0);
      mem_data_o           : out std_logic_vector(DRAM_IO_DWIDTH-1 downto 0)
   );
end entity ComBlock;

architecture RTL of ComBlock is

   constant REGS_FIFO_DEPTH : positive := 7;

   signal rd_sel, wr_sel    : std_logic_vector(1 downto 0);
   signal rd_idx, wr_idx    : natural range 0 to 15;

   type regs_type is array (natural range <>) of std_logic_vector(31 downto 0);
   signal regs_in           : regs_type(0 to 15)                := (others => (others => '0'));
   signal regs_out          : regs_type(0 to 15)                := (others => (others => '0'));
   signal regs_fifo         : regs_type(0 to REGS_FIFO_DEPTH-1) := (others => (others => '0'));

   -- fifo in
   signal fifo_in_clear     : std_logic;
   signal fifo_in_re        : std_logic;
   signal fifo_in_data      : std_logic_vector(FIFO_IN_DWIDTH-1 downto 0);
   signal fifo_in_valid     : std_logic;
   signal fifo_in_empty     : std_logic;
   signal fifo_in_aempty    : std_logic;
   signal fifo_in_under     : std_logic;
   signal fifo_in_under_r   : std_logic:='0';
   signal fifo_in_count     : std_logic_vector(15 downto 0);

   -- fifo out
   signal fifo_out_clear    : std_logic;
   signal fifo_out_we       : std_logic;
   signal fifo_out_data     : std_logic_vector(FIFO_OUT_DWIDTH-1 downto 0);
   signal fifo_out_full     : std_logic;
   signal fifo_out_afull    : std_logic;
   signal fifo_out_over     : std_logic;
   signal fifo_out_over_r   : std_logic:='0';
   signal fifo_out_count    : std_logic_vector(15 downto 0);

begin

   -- -------------------------------------------------------------------------
   -- Registers - FPGA side
   -- -------------------------------------------------------------------------

   regs_in(0)(REGS_IN_DWIDTH-1 downto 0)  <= reg0_i;
   regs_in(1)(REGS_IN_DWIDTH-1 downto 0)  <= reg1_i;
   regs_in(2)(REGS_IN_DWIDTH-1 downto 0)  <= reg2_i;
   regs_in(3)(REGS_IN_DWIDTH-1 downto 0)  <= reg3_i;
   regs_in(4)(REGS_IN_DWIDTH-1 downto 0)  <= reg4_i;
   regs_in(5)(REGS_IN_DWIDTH-1 downto 0)  <= reg5_i;
   regs_in(6)(REGS_IN_DWIDTH-1 downto 0)  <= reg6_i;
   regs_in(7)(REGS_IN_DWIDTH-1 downto 0)  <= reg7_i;
   regs_in(8)(REGS_IN_DWIDTH-1 downto 0)  <= reg8_i;
   regs_in(9)(REGS_IN_DWIDTH-1 downto 0)  <= reg9_i;
   regs_in(10)(REGS_IN_DWIDTH-1 downto 0) <= reg10_i;
   regs_in(11)(REGS_IN_DWIDTH-1 downto 0) <= reg11_i;
   regs_in(12)(REGS_IN_DWIDTH-1 downto 0) <= reg12_i;
   regs_in(13)(REGS_IN_DWIDTH-1 downto 0) <= reg13_i;
   regs_in(14)(REGS_IN_DWIDTH-1 downto 0) <= reg14_i;
   regs_in(15)(REGS_IN_DWIDTH-1 downto 0) <= reg15_i;

   reg0_o  <= regs_out(0)(REGS_OUT_DWIDTH-1 downto 0);
   reg1_o  <= regs_out(1)(REGS_OUT_DWIDTH-1 downto 0);
   reg2_o  <= regs_out(2)(REGS_OUT_DWIDTH-1 downto 0);
   reg3_o  <= regs_out(3)(REGS_OUT_DWIDTH-1 downto 0);
   reg4_o  <= regs_out(4)(REGS_OUT_DWIDTH-1 downto 0);
   reg5_o  <= regs_out(5)(REGS_OUT_DWIDTH-1 downto 0);
   reg6_o  <= regs_out(6)(REGS_OUT_DWIDTH-1 downto 0);
   reg7_o  <= regs_out(7)(REGS_OUT_DWIDTH-1 downto 0);
   reg8_o  <= regs_out(8)(REGS_OUT_DWIDTH-1 downto 0);
   reg9_o  <= regs_out(9)(REGS_OUT_DWIDTH-1 downto 0);
   reg10_o <= regs_out(10)(REGS_OUT_DWIDTH-1 downto 0);
   reg11_o <= regs_out(11)(REGS_OUT_DWIDTH-1 downto 0);
   reg12_o <= regs_out(12)(REGS_OUT_DWIDTH-1 downto 0);
   reg13_o <= regs_out(13)(REGS_OUT_DWIDTH-1 downto 0);
   reg14_o <= regs_out(14)(REGS_OUT_DWIDTH-1 downto 0);
   reg15_o <= regs_out(15)(REGS_OUT_DWIDTH-1 downto 0);

   -- -------------------------------------------------------------------------
   -- True Dual Port RAM
   -- -------------------------------------------------------------------------

   dram_g : if DRAM_IO_ENA generate
      dram_i: entity work.tdpram
      generic map (
         AWIDTH   => DRAM_IO_AWIDTH,
         DWIDTH   => DRAM_IO_DWIDTH,
         DEPTH    => DRAM_IO_DEPTH
      )
      port map (
         -- FPGA side
         clk1_i   => ram_clk_i,
         wen1_i   => ram_we_i,
         addr1_i  => ram_addr_i,
         data1_i  => ram_data_i,
         data1_o  => ram_data_o,
         -- PROC side
         clk2_i   => mem_clk_i,
         wen2_i   => mem_we_i,
         addr2_i  => mem_addr_i,
         data2_i  => mem_data_i,
         data2_o  => mem_data_o
      );
   end generate;

   -- -------------------------------------------------------------------------
   -- FIFOs
   -- -------------------------------------------------------------------------

   fifo_in_g : if FIFO_IN_ENA generate

      fifo_in_i: entity work.fifo
      generic map (
         DWIDTH       => FIFO_IN_DWIDTH,
         DEPTH        => FIFO_IN_DEPTH,
         AEMPTYOFFSET => FIFO_IN_AEOFFSET,
         AFULLOFFSET  => FIFO_IN_AFOFFSET
      )
      port map (
         -- FPGA (write) side
         wclk_i       => fifo_in_clk_i,
         wrst_i       => fifo_in_clear_i,
         wen_i        => fifo_in_we_i,
         data_i       => fifo_in_data_i,
         full_o       => fifo_in_full_o,
         afull_o      => fifo_in_afull_o,
         overflow_o   => fifo_in_overflow_o,
         -- PROC (read) side
         rclk_i       => reg_clk_i,
         rrst_i       => fifo_in_clear,
         ren_i        => fifo_in_re,
         data_o       => fifo_in_data,
         empty_o      => fifo_in_empty,
         aempty_o     => fifo_in_aempty,
         underflow_o  => fifo_in_under,
         valid_o      => fifo_in_valid,
         rcount_o     => fifo_in_count
      );

      fifo_in_re <= reg_rd_ena_i when rd_sel = "10" and rd_idx = 0 else '0';

   end generate;

   fifo_out_g : if FIFO_OUT_ENA generate

      fifo_out_i: entity work.fifo
      generic map (
         DWIDTH       => FIFO_OUT_DWIDTH,
         DEPTH        => FIFO_OUT_DEPTH,
         AEMPTYOFFSET => FIFO_OUT_AEOFFSET,
         AFULLOFFSET  => FIFO_OUT_AFOFFSET
      )
      port map (
         -- FPGA (read) side
         rclk_i       => fifo_out_clk_i,
         rrst_i       => fifo_out_clear_i,
         ren_i        => fifo_out_re_i,
         data_o       => fifo_out_data_o,
         empty_o      => fifo_out_empty_o,
         aempty_o     => fifo_out_aempty_o,
         underflow_o  => fifo_out_underflow_o,
         valid_o      => fifo_out_valid_o,
         -- PROC (write) side
         wclk_i       => reg_clk_i,
         wrst_i       => fifo_out_clear,
         wen_i        => fifo_out_we,
         data_i       => fifo_out_data,
         full_o       => fifo_out_full,
         afull_o      => fifo_out_afull,
         overflow_o   => fifo_out_over,
         wcount_o     => fifo_out_count
      );

      fifo_out_data <= reg_wr_data_i(FIFO_OUT_DWIDTH-1 downto 0); -- FIFO_OUT_VALUE
      fifo_out_we   <= reg_wr_ena_i when wr_sel = "10" and wr_idx = 4 else '0';

   end generate;

   -- -------------------------------------------------------------------------
   -- FIFO registers (see doc/registers.md for more information) - PROC side
   -- -------------------------------------------------------------------------

   -- FIFO_IN_VALUE
   fifo0_gen : if FIFO_IN_ENA generate
      regs_fifo(0)(FIFO_IN_DWIDTH-1 downto 0) <= fifo_in_data;
   end generate fifo0_gen;
   not_fifo0_gen : if not FIFO_IN_ENA generate
      regs_fifo(0) <= (others => '0');
   end generate not_fifo0_gen;

   -- FIFO_IN_CONTROL
   -- Is written by the processor.

   -- FIFO_IN_STATUS
   fifo2_gen : if FIFO_IN_ENA generate
      regs_fifo(2)(31 downto 16) <= fifo_in_count;
      regs_fifo(2)(15 downto  3) <= (others => '0');
      regs_fifo(2)(2)            <= fifo_in_under_r;
      regs_fifo(2)(1)            <= fifo_in_aempty;
      regs_fifo(2)(0)            <= fifo_in_empty;
   end generate fifo2_gen;
   not_fifo2_gen : if not FIFO_IN_ENA generate
      regs_fifo(2) <= (others => '0');
   end generate not_fifo2_gen;

   -- FIFO_OUT_VALUE
   -- FIFO_OUT_CONTROL
   -- Are written by the processor.

   -- FIFO_OUT_STATUS
   fifo3_gen : if FIFO_OUT_ENA generate
      regs_fifo(6)(31 downto 16) <= fifo_out_count;
      regs_fifo(6)(15 downto  3) <= (others => '0');
      regs_fifo(6)(2)            <= fifo_out_over_r;
      regs_fifo(6)(1)            <= fifo_out_afull;
      regs_fifo(6)(0)            <= fifo_out_full;
   end generate fifo3_gen;
   not_fifo3_gen : if not FIFO_OUT_ENA generate
      regs_fifo(6) <= (others => '0');
   end generate not_fifo3_gen;

   -- -------------------------------------------------------------------------
   -- Mapping - PROC side
   -- -------------------------------------------------------------------------

   rd_sel <= reg_rd_addr_i(5 downto 4);
   rd_idx <= to_integer(unsigned(reg_rd_addr_i(3 downto 0)));

   wr_sel <= reg_wr_addr_i(5 downto 4);
   wr_idx <= to_integer(unsigned(reg_wr_addr_i(3 downto 0)));

   reg_rd_data_o <=
      regs_in(rd_idx)   when rd_sel="00" and rd_idx < REGS_IN_DEPTH   else
      regs_out(rd_idx)  when rd_sel="01" and rd_idx < REGS_OUT_DEPTH  else
      regs_fifo(rd_idx) when rd_sel="10" and rd_idx < REGS_FIFO_DEPTH else
      (others => '0');

   do_write : process(reg_clk_i)
   begin
      if rising_edge(reg_clk_i) then
         fifo_out_clear <= '0';
         fifo_in_clear  <= '0';
         if reg_wr_ena_i = '1' then
            if REGS_OUT_ENA and wr_sel = "01" then
               if wr_idx < REGS_OUT_DEPTH then
                  regs_out(wr_idx) <= reg_wr_data_i(REGS_OUT_DWIDTH-1 downto 0);
               end if;
            end if;
            if wr_sel = "10" then
               if FIFO_IN_ENA and wr_idx = 1 then
                  fifo_in_clear  <= '1';
               end if;
               if FIFO_OUT_ENA and wr_idx = 5 then
                  fifo_out_clear <= '1';
               end if;
            end if;
         end if;
         --
         if fifo_in_under = '1' then
            fifo_in_under_r <= '1';
         end if;
         if fifo_out_over = '1' then
            fifo_out_over_r <= '1';
         end if;
         if reg_rd_ena_i = '1' then
            if rd_sel = "10" then
               if FIFO_IN_ENA and rd_idx = 2 then
                  fifo_in_under_r <= '0';
               end if;
               if FIFO_OUT_ENA and rd_idx = 6 then
                  fifo_out_over_r <= '0';
               end if;
            end if;
         end if;
      end if;
   end process do_write;

end architecture RTL;
