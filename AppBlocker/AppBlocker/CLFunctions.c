//
//  CLFunctions.c
//  AppBlocker
//
//  Created by jayke on 6/17/19.
//  Copyright © 2019 Jayke Peters. All rights reserved.
//

#include "CLFunctions.h"

char * getRootProcessPathUsingPID(pid_t pid) {
    int ret;
    char pathbuf[PROC_PIDPATHINFO_MAXSIZE];
    
    ret = proc_pidpath (pid, pathbuf, sizeof(pathbuf));
    if (ret <= 0) {
        fprintf(stderr, "PID %d: proc_pidpath ();\n", pid);
        fprintf(stderr, "    %s\n", strerror(errno));
        return 1;
        
        } else {
            printf("%s", pathbuf);
        }
    return pathbuf; // as mem adress to char or just char??
}
