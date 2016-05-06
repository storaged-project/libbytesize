#ifndef _BS_SIZE_H
#define _BS_SIZE_H

#include <stdint.h>
#include <stdbool.h>

/**
 * BSSize:
 * An opaque type representing a size in bytes.
 */
typedef struct _BSSize * BSSize;

/**
 * BSErrorCode:
 *
 * @BS_ERROR_INVALID_SPEC: invalid size or unit spec provided
 * @BS_ERROR_OVER: a value is over the limits imposed by a type
 * @BS_ERROR_ZERO_DIV: an attempt to do division by zero
 *
 * Error codes that identify various errors that can occur while working with
 * #BSSize instances.
 */
typedef enum {
    BS_ERROR_INVALID_SPEC,
    BS_ERROR_OVER,
    BS_ERROR_ZERO_DIV,
    BS_ERROR_FAIL
} BSErrorCode;

/**
 * BSError:
 *
 * @code: error code
 * @msg: optional error message
 */
typedef struct _BSError {
    BSErrorCode code;
    char *msg;
} BSError;

/**
 * BSBunit:
 *
 * Binary units (multiples of 1024) of size in bytes.
 */
typedef enum {
    BS_BUNIT_B = 0, BS_BUNIT_KiB, BS_BUNIT_MiB, BS_BUNIT_GiB, BS_BUNIT_TiB,
    BS_BUNIT_PiB, BS_BUNIT_EiB, BS_BUNIT_ZiB, BS_BUNIT_YiB, BS_BUNIT_UNDEF,
} BSBunit;

/**
 * BSDunit:
 *
 * Decimal units (multiples of 1000) of size in bytes.
 */
typedef enum {
    BS_DUNIT_B = 20, BS_DUNIT_KB, BS_DUNIT_MB, BS_DUNIT_GB, BS_DUNIT_TB,
    BS_DUNIT_PB, BS_DUNIT_EB, BS_DUNIT_ZB, BS_DUNIT_YB, BS_DUNIT_UNDEF,
} BSDunit;

/**
 * BSRoundDir:
 *
 * Rounding direction for rounding operations.
 */
typedef enum {
    BS_ROUND_DIR_UP = 0,
    BS_ROUND_DIR_DOWN = 1,
    BS_ROUND_DIR_HALF_UP = 2
} BSRoundDir;

/**
 * BSUnit:
 * @bunit: a binary unit
 * @dunit: a decimal unit
 *
 * Generic unit fo size in bytes.
 */
typedef union {
    BSBunit bunit;
    BSDunit dunit;
} BSUnit;

/* use 256 bits of precision for floating point numbets, that should be more
   than enough */
/**
 * BS_FLOAT_PREC_BITS:
 *
 * Precision (in bits) of floating-point numbers used internally.
 */
#define BS_FLOAT_PREC_BITS 256

/* Constructors */
BSSize bs_size_new (void);
BSSize bs_size_new_from_bytes (uint64_t bytes, int sgn);
BSSize bs_size_new_from_str (const char *size_str, BSError **error);
BSSize bs_size_new_from_size (const BSSize size);

/* Destructors */
void bs_size_free (BSSize size);
void bs_clear_error (BSError **error);

/* Query functions */
uint64_t bs_size_get_bytes (const BSSize size, int *sgn, BSError **error);
int bs_size_sgn (const BSSize size);
char* bs_size_get_bytes_str (const BSSize size);
char* bs_size_convert_to (const BSSize size, BSUnit unit, BSError **error);
char* bs_size_human_readable (const BSSize size, BSBunit min_unit, int max_places, bool xlate);

/* Arithmetic */
BSSize bs_size_add (const BSSize size1, const BSSize size2);
BSSize bs_size_grow (BSSize size1, const BSSize size2);
BSSize bs_size_add_bytes (const BSSize size, uint64_t bytes);
BSSize bs_size_grow_bytes (BSSize size, uint64_t bytes);
BSSize bs_size_sub (const BSSize size1, const BSSize size2);
BSSize bs_size_shrink (BSSize size1, const BSSize size2);
BSSize bs_size_sub_bytes (const BSSize size, uint64_t bytes);
BSSize bs_size_shrink_bytes (BSSize size, uint64_t bytes);
BSSize bs_size_mul_int (const BSSize size, uint64_t times);
BSSize bs_size_grow_mul_int (BSSize size, uint64_t times);
BSSize bs_size_mul_float_str (const BSSize size, const char *float_str, BSError **error);
BSSize bs_size_grow_mul_float_str (BSSize size, const char *float_str, BSError **error);
uint64_t bs_size_div (const BSSize size1, const BSSize size2, int *sgn, BSError **error);
BSSize bs_size_div_int (const BSSize size, uint64_t divisor, BSError **error);
BSSize bs_size_shrink_div_int (BSSize size, uint64_t shrink_divisor, BSError **error);
char* bs_size_true_div (const BSSize size1, const BSSize size2, BSError **error);
char* bs_size_true_div_int (const BSSize size, uint64_t divisor, BSError **error);
BSSize bs_size_mod (const BSSize size1, const BSSize size2, BSError **error);
BSSize bs_size_round_to_nearest (const BSSize size, const BSSize round_to, BSRoundDir dir, BSError **error);

/* Comparisons */
int bs_size_cmp (const BSSize size1, const BSSize size2, bool abs);
int bs_size_cmp_bytes (const BSSize size1, uint64_t bytes, bool abs);

#endif  /* _BS_SIZE_H */
