DIRS = $(wildcard */)

all:
	@$(foreach DIR,$(DIRS),make -C $(DIR);)

clean:
	@$(foreach DIR,$(DIRS),make -C $(DIR) clean;)
