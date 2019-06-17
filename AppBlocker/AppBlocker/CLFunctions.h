//
//  CLFunctions.h
//  AppBlocker
//
//  Created by jayke on 6/17/19.
//  Copyright © 2019 Jayke Peters. All rights reserved.
//

#ifndef CLFunctions_h
#define CLFunctions_h

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <libproc.h>

char * getRootProcessPathUsingPID(pid_t pid);

#endif /* CLFunctions_h */
