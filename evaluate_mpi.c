#include<stdio.h>
#include<stdlib.h>
#include"mpi.h"

#define BUF_LEN 839
#define ITER 10000

int main(int argc , char *argv[]) {
    MPI_Init(&argc, &argv);
    int rank,size;

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    char DATA[BUF_LEN] = "AWMsswedfpwelsdfsdsvgedvgdgdfgdfgrggrggrtgtrgtrhhtyijynuikt7yikujmfghnfbvdghngjngngngfrtarkctv,[serotgjrodfpghmdrohrffdhjrtdhpiodfrh,jththjmthtjnmhtyihnityhtyhtyhtyohbnmtyihoyutnjhitujnhytihyutnytediotuihgbnetrihmgbosv.fk,djmbgmhnrfkecl.ds,kvmgjbhifkdcfderfgtyyhgvcdrthygfvzsdfrfgvtdgvfhdvdfvdhvdvsdefgvsdgesrgser g[ serbigsergjmriopseeopscrvi,serri,eo.cgjnriosgnrsi.gnropegrdngbhrg brgterbhertbhtydrhbdt bhtdfrbhdftyr hvtydfhb ctydfhc tdfrch tvdyhy cvtdh cvftydhnypifso[jmsepergjiasogejgoperjspgoseopgserjgpjsergserghjrsp[hjdrt p0[hiorjp[h iojdrthioprtyjdhiopdrtjmhopidrtjmhoirtyjdmhodrtjhopdrtjihopdrtjmhopdrtihjrdthorydtkhj[oh ikq-]ru0t9 yu=q2459uyn=24v 5t9.sec korgter6thnreitynuhteyhunmety0hnmbertyiokgb,wlp.dfv;'/sadlrbikegjovld;.cs,v fbmgjikftorlfpdsxa.cz,vmnfbgdjrkdes,lxcvmfngjrkedsl,xcvmfgtrkedlsd,fmgjrkdsl,fcmvngjmdrke,sf]]]]";
    double total_time = 0;
    for(int i=0 ; i<ITER ; i++) {
        double t = MPI_Wtime();
        MPI_Bcast(DATA, BUF_LEN, MPI_CHAR, 0, MPI_COMM_WORLD);
        total_time += MPI_Wtime() - t;
    }

    if(rank == 0) {
        printf("Average time taken for MPI_Bcast: %lf\n", total_time/ITER);
    }
    

}