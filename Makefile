.PHONY: run clean mpirun_r mpirun mpicom mpiclean i_mpirun_r i_mpirun i_mpicom i_mpirun_r4 i_mpirun_r6

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
	rm a.out
	/opt/mpich/bin/mpicc mpi_ip.c

mpirun_r6:
	/opt/mpich/bin/mpirun --np 24 --hostfile hosts.txt ./a.out

mpirun_r4:
	/opt/mpich/bin/mpirun --np 24 --hostfile hosts_v4.txt ./a.out

mpirun:
	/opt/mpich/bin/mpirun --np 4 ./a.out

i_mpicom:
	rm a.out
	/opt/intel/oneapi/mpi/2021.12/bin/mpiicx mpi_ip.c

i_mpirun_r6:
	/opt/intel/oneapi/mpi/2021.12/bin/mpirun --np 12 --hostfile hosts.txt a.out

i_mpirun_r4:
	/opt/intel/oneapi/mpi/2021.12/bin/mpirun --np 24 --hostfile hosts_v4.txt ./a.out

i_mpirun:
	/opt/intel/oneapi/mpi/2021.12/bin/mpirun --np 4 ./a.out

mpiclean:
	rm a.out