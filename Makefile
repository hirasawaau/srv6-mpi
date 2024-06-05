.PHONY: run clean mpirun_r4 mpirun mpicom mpiclean mpirun_r6 mpipwd_r6 mpipwd_r4

run:
	@echo "Running the program..."
	python3 main.py
	mn -c

mini_run:
	@echo "Running the program..."
	python3 mini_topo.py

clean:
	@echo "Cleaning Dump"
	rm -rf ./dump/*.pcap

mpicom:
	-rm a.out
	/opt/ompi/bin/mpicc evaluate_mpi.c

mpirun_r6:
	/opt/ompi/bin/mpirun --np 24 --allow-run-as-root --hostfile hosts.txt ./a.out

mpirun_r4:
	/opt/ompi/bin/mpirun --np 16 --allow-run-as-root --hostfile hosts_v4.txt --mca oob_base_verbose 100 --mca btl_base_verbose 100 ./a.out

mpipwd_r6:
	/opt/ompi/bin/mpirun --np 16 --allow-run-as-root --hostfile hosts.txt --mca tcp6 ./a.o

mpipwd_r4:
	/opt/ompi/bin/mpirun --np 16 --allow-run-as-root --hostfile hosts_v4.txt --mca oob_base_verbose 100 --mca btl_base_verbose 100 pwd

mpiclean:
	rm a.out