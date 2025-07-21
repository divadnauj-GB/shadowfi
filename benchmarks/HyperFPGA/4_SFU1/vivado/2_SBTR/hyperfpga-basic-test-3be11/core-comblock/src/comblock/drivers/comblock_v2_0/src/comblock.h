#ifndef COMBLOCK_H
#define COMBLOCK_H

#include <string.h>

//
// Defines
//

#define CB_IREG0             0
#define CB_IREG1             1
#define CB_IREG2             2
#define CB_IREG3             3
#define CB_IREG4             4
#define CB_IREG5             5
#define CB_IREG6             6
#define CB_IREG7             7
#define CB_IREG8             8
#define CB_IREG9             9
#define CB_IREG10            10
#define CB_IREG11            11
#define CB_IREG12            12
#define CB_IREG13            13
#define CB_IREG14            14
#define CB_IREG15            15

#define CB_OREG0             16
#define CB_OREG1             17
#define CB_OREG2             18
#define CB_OREG3             19
#define CB_OREG4             20
#define CB_OREG5             21
#define CB_OREG6             22
#define CB_OREG7             23
#define CB_OREG8             24
#define CB_OREG9             25
#define CB_OREG10            26
#define CB_OREG11            27
#define CB_OREG12            28
#define CB_OREG13            29
#define CB_OREG14            30
#define CB_OREG15            31

#define CB_IFIFO_VALUE       32
#define CB_IFIFO_CONTROL     33
#define CB_IFIFO_STATUS      34

// RFU: 35

#define CB_OFIFO_VALUE       36
#define CB_OFIFO_CONTROL     37
#define CB_OFIFO_STATUS      38

// RFU: 39, 40:63

//
// Types
//

typedef __UINTPTR_TYPE__ UINTPTR;
typedef __UINT32_TYPE__  u32;

//
// Functions
//

static inline void cbWrite(UINTPTR baseaddr, u32 reg, u32 value) {
   volatile u32 *addr = (volatile u32 *)(baseaddr + reg*4);
   *addr = value;
}

static inline u32 cbRead(UINTPTR baseaddr, u32 reg) {
   return *(volatile u32 *)(baseaddr + reg*4);
}

static inline void cbWriteBulk(UINTPTR baseaddr, int *buffer, u32 depth) {
   memcpy((UINTPTR *)baseaddr, buffer, depth * sizeof(int));
}

static inline void cbReadBulk(int *buffer, UINTPTR baseaddr, u32 depth) {
   memcpy(buffer, (UINTPTR *)baseaddr, depth * sizeof(int));
}

#endif // COMBLOCK_H
