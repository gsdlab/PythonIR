SRC_DIR  := src

all:
	# Create the Egg
	$(MAKE) -C $(SRC_DIR)

init:
	# Copy Z3
	@if [ -z $(z3bin) ]; then \
		echo "Provide the path to Z3 SMT solver's bin (or build) folder to 'z3bin' flag";  \
		read z3bin; \
	fi
	cp $(z3bin)/*.* src

install:
	mkdir -p $(to)
	cp -f README.md $(to)/ClaferSMT-README.md
	cp -f claferSMT.egg $(to)	