-- barrel shifter.
-- desplazamiento izquierdo.
Library IEEE;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity punto1 is 
generic(
		long : natural := 64;
		v1:natural := 2;
		v2:natural := 4;
		v3:natural := 8;
		v4:natural := 16;
		bass : natural := 2
		);
     
port(
	entrada_real: in unsigned(long-1 downto 0);
	shift: in unsigned(6 downto 0);
	salida_real: out unsigned(23 downto 0)
	);
end punto1;

architecture ar of punto1 is

    type vector is array (0 to 5,0 to long-1) of std_logic;	-- (0 a log de # bits, long de Bit)
    signal var: vector;
    signal entrada, salida,salida_inv: unsigned(long-1 downto 0);

	component mux2_1 is 
	port(
		x,y,s: in  std_logic;
		z: out std_logic
		);
	end component;

	type vec is array (0 to 7) of natural;
	signal basse: vec :=(v1 ,v2 ,v3 ,v4 ,8 ,16 ,32 ,64);

begin

		-- agregado para hacer inversion de dato de entrada.

		ENTRADAX:for i in 0 to long-1 generate
			entrada(i)<= entrada_real(long-1-i);
			salida_inv(i)<= salida(long-1-i);
		end generate;

		SALIDAX:for i in 0 to 23 generate		-- para esta aplicacion solo se tomas los 23 datos.
			salida_real(i)<= salida_inv(i);
		end generate;


	    	    
   	    GENX:for i in 0 to long-1 generate
			
			PART_B: if i< 1 generate
			MU: mux2_1 port map(
								x=>entrada(0),
								y=>'0',
								s=>shift(0),
								z=>var(0,0)
								);			
			end generate PART_B;
				
			PART_A: if i >= 1 generate
			MU: mux2_1 port map(x=>entrada(i),
								y=>entrada(i-1),
								s=>shift(0),
								z=>var(0,i)
								); 			
			end generate PART_A;
											
		end generate GENX;

		--capa 2		

	GENA:for i in 0 to long-1 generate
		
		PART_B1: if i < 2 generate
			MX0:mux2_1 port map(x=>var(0,i),
								y=>'0',
								s=>shift(1),
								z=>var(1,i)	
								); 
		end generate PART_B1;

		PART_A1: if i >= 2 generate
			MY: mux2_1 port map(x=>var(0,i),
					y=>var(0,i-2),
					s=>shift(1),
				    z=>var(1,i)
					);
		end generate PART_A1;
	end generate GENA;


		--capa 3


	GENA1:for i in 0 to long-1 generate
		
		PART_B1: if i < 4 generate
			MX0:mux2_1 port map(x=>var(1,i),
								y=>'0',
								s=>shift(2),
								z=>var(2,i)	
								); 
		end generate PART_B1;

		PART_A1: if i >= 4 generate
			MY: mux2_1 port map(x=>var(1,i),
					y=>var(1,i-4),
					s=>shift(2),
				    z=>var(2,i)
					);
		end generate PART_A1;
	end generate GENA1;

	--capa 4

	GENA2:for i in 0 to long-1 generate
		
		PART_B1: if i < 8 generate
			MX0:mux2_1 port map(x=>var(2,i),
								y=>'0',
								s=>shift(3),
								z=>var(3,i)	
								); 
		end generate PART_B1;

		PART_A1: if i >= 8 generate
			MY: mux2_1 port map(x=>var(2,i),
					y=>var(2,i-8),
					s=>shift(3),
				    z=>var(3,i)
					);
		end generate PART_A1;
	end generate GENA2;

		--capa5
	GENA3:for i in 0 to long-1 generate
		
		PART_B1: if i < 16 generate
			MX0:mux2_1 port map(x=>var(3,i),
								y=>'0',
								s=>shift(4),
								z=>var(4,i)	
								); 
		end generate PART_B1;

		PART_A1: if i >= 16 generate
			MY: mux2_1 port map(x=>var(3,i),
					y=>var(3,i-16),
					s=>shift(4),
				    z=>var(4,i)
					);
		end generate PART_A1;
	end generate GENA3;

		--capa 6
	GENB:for i in 0 to long-1 generate
		
		PART_Bx: if i < 32 generate
		
		MW0:mux2_1 port map(x=>var(4,i),
					y=>'0',
					s=>shift(5),
				    z=>salida(i)
					); 			
		
		end generate PART_Bx;		
				
		PART_Ax: if i >= 32 generate
		
 		MZ: mux2_1 port map(x=>var(4,i),
					y=>var(4,i-32),
					s=>shift(5),
				    z=>salida(i)
					);
		end generate PART_Ax;				
	end generate GENB;
end ar;
