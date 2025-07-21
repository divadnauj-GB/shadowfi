library IEEE;
use IEEE.std_logic_1164.all;

entity fifo_loop is
   generic (
      WIDTH   : positive := 16
   );
   port (
      clk_i   :  in std_logic;
      data_i  :  in std_logic_vector(WIDTH-1 downto 0);
      empty_i :  in std_logic;
      valid_i :  in std_logic;
      re_o    : out std_logic;
      we_o    : out std_logic;
      data_o  : out std_logic_vector(WIDTH-1 downto 0);
      full_i  :  in std_logic
   );
end entity fifo_loop;

architecture Structural of fifo_loop is
begin

   we_o   <= valid_i;
   data_o <= data_i;

   process (clk_i)
   begin
      if rising_edge(clk_i) then
         re_o <= '0';
         if empty_i='0' and full_i = '0' then
            re_o <= '1';
         end if;
      end if;
   end process;

end architecture Structural;
