#include <gmp.h>
#include <mpfr.h>
#include <langinfo.h>
#include <stdarg.h>
#include <stdio.h>
#include <inttypes.h>
#include <string.h>
#include <ctype.h>
#include <limits.h>
#include <pcre.h>

#include "bs_size.h"
#include "gettext.h"

#define  _(String) gettext (String)
#define N_(String) String

/**
 * SECTION: bs_size
 * @title: BSSize
 * @short_description: a class facilitating work with sizes in bytes
 * @include: bs_size.h
 *
 * #BSSize is a type that facilitates work with sizes in bytes by providing
 * functions/methods that are required for parsing users input when entering
 * size, showing size in nice human-readable format, storing sizes bigger than
 * %UINT64_MAX and doing calculations with sizes without loss of
 * precision/information. The class is able to hold negative sizes and do
 * operations on/with them, but some of the (division and multiplication)
 * operations simply ignore the signs of the operands (check the documentation).
 *
 * The reason why some functions take or return a float as a string instead of a
 * float directly is because a string "0.3" can be translated into 0.3 with
 * appropriate precision while 0.3 as float is probably something like
 * 0.294343... with unknown precision.
 *
 */


/***************
 * STATIC DATA *
 ***************/
static char const * const b_units[BS_BUNIT_UNDEF] = {
    /* TRANSLATORS: 'B' for bytes */
    N_("B"),
    /* TRANSLATORS: abbreviation for kibibyte, 2**10 bytes */
    N_("KiB"),
    /* TRANSLATORS: abbreviation for mebibyte, 2**20 bytes */
    N_("MiB"),
    /* TRANSLATORS: abbreviation for gibibyte, 2**30 bytes */
    N_("GiB"),
    /* TRANSLATORS: abbreviation for tebibyte, 2**40 bytes */
    N_("TiB"),
    /* TRANSLATORS: abbreviation for pebibyte, 2**50 bytes */
    N_("PiB"),
    /* TRANSLATORS: abbreviation for exbibyte, 2**60 bytes */
    N_("EiB"),
    /* TRANSLATORS: abbreviation for zebibyte, 2**70 bytes */
    N_("ZiB"),
    /* TRANSLATORS: abbreviation for yobibyte, 2**80 bytes */
    N_("YiB")
};

static char const * const d_units[BS_DUNIT_UNDEF] = {
    /* TRANSLATORS: 'B' for bytes */
    N_("B"),
    /* TRANSLATORS: abbreviation for kilobyte, 10**3 bytes */
    N_("KB"),
    /* TRANSLATORS: abbreviation for megabyte, 10**6 bytes */
    N_("MB"),
    /* TRANSLATORS: abbreviation for gigabyte, 10**9 bytes */
    N_("GB"),
    /* TRANSLATORS: abbreviation for terabyte, 10**12 bytes */
    N_("TB"),
    /* TRANSLATORS: abbreviation for petabyte, 10**15 bytes */
    N_("PB"),
    /* TRANSLATORS: abbreviation for exabyte, 10**18 bytes */
    N_("EB"),
    /* TRANSLATORS: abbreviation for zettabyte, 10**21 bytes */
    N_("ZB"),
    /* TRANSLATORS: abbreviation for yottabyte, 10**24 bytes */
    N_("YB")
};


/****************************
 * STRUCT DEFINITIONS       *
 ****************************/
/**
 * BSSize:
 *
 * The BSSize struct contains only private fields and should not be directly
 * accessed.
 */
struct _BSSize {
    mpz_t bytes;
};


/********************
 * HELPER FUNCTIONS *
 ********************/
static void bs_size_init (BSSize size) {
    /* let's start with 64 bits of space */
    mpz_init2 (size->bytes, (mp_bitcnt_t) 64);
}

static char *strdup_printf (const char *fmt, ...) {
    int num = 0;
    char *ret = NULL;
    va_list ap;
    va_start (ap, fmt);
    num = vasprintf (&ret, fmt, ap);
    va_end (ap);
    if (num <= 0)
        /* make sure we return NULL on error */
        ret = NULL;
    return ret;
}

/**
 * replace_char_with_str: (skip)
 *
 * Replaces all apperances of @char in @str with @new.
 */
static char *replace_char_with_str (const char *str, char orig, const char *new) {
    uint64_t offset = 0;
    uint64_t i = 0;
    uint64_t j = 0;
    char *ret = NULL;
    const char *next = NULL;
    uint64_t count = 0;

    if (!str)
        return NULL;

    next = str;
    for (next=strchr (next, orig); next; count++, next=strchr (++next, orig));

    /* allocate space for the string [strlen(str)] with the char replaced by the
       string [strlen(new) - 1] $count times and a \0 byte at the end [ + 1] */
    ret = malloc (sizeof(char) * (strlen(str) + (strlen(new) - 1) * count + 1));

    for (i=0; str[i]; i++) {
        if (str[i] == orig)
            for (j=0; new[j]; j++) {
                ret[i+offset] = new[j];
                if (new[j+1])
                    /* something more to copy over */
                    offset++;
            }
        else
            ret[i+offset] = str[i];
    }
    ret[i+offset] = '\0';

    return ret;
}


/**
 * replace_str_with_str: (skip)
 *
 * Replaces the first appearance of @orig in @str with @new.
 */
static char *replace_str_with_str (const char *str, const char *orig, const char *new) {
    char *pos = NULL;
    int str_len = 0;
    int orig_len = 0;
    int new_len = 0;
    char *ret = NULL;
    int ret_size = 0;
    char *dest = NULL;

    pos = strstr (str, orig);
    if (!pos)
        /* nothing to do, just return a copy */
        return strdup (str);

    str_len = strlen (str);
    orig_len = strlen (orig);
    new_len = strlen (new);
    ret_size = str_len + new_len - orig_len + 1;
    ret = malloc (sizeof(char) * ret_size);
    memset (ret, 0, ret_size);
    memcpy (ret, str, pos - str);
    dest = ret + (pos - str);
    memcpy (dest, new, new_len);
    dest = dest + new_len;
    memcpy (dest, pos + orig_len, str_len - (pos - str) - orig_len);

    return ret;
}

/**
 * strstrip: (skip)
 *
 * Strips leading and trailing whitespace from the string (**IN-PLACE**)
 */
static void strstrip(char *str) {
    int i = 0;
    int begin = 0;
    int end = strlen(str) - 1;

    while (isspace(str[begin]))
        begin++;
    while ((end >= begin) && isspace(str[end]))
        end--;

    for (i=begin; i <= end; i++)
        str[i - begin] = str[i];

    str[i-begin] = '\0';
}

static bool multiply_size_by_unit (mpfr_t size, char *unit_str) {
    BSBunit bunit = BS_BUNIT_UNDEF;
    BSDunit dunit = BS_DUNIT_UNDEF;
    uint64_t pwr = 0;
    mpfr_t dec_mul;
    size_t unit_str_len = 0;

    unit_str_len = strlen (unit_str);

    for (bunit=BS_BUNIT_B; bunit < BS_BUNIT_UNDEF; bunit++)
        if (strncasecmp (unit_str, b_units[bunit-BS_BUNIT_B], unit_str_len) == 0) {
            pwr = (uint64_t) bunit - BS_BUNIT_B;
            mpfr_mul_2exp (size, size, 10 * pwr, MPFR_RNDN);
            return true;
        }

    mpfr_init2 (dec_mul, BS_FLOAT_PREC_BITS);
    mpfr_set_ui (dec_mul, 1000, MPFR_RNDN);
    for (dunit=BS_DUNIT_B; dunit < BS_DUNIT_UNDEF; dunit++)
        if (strncasecmp (unit_str, d_units[dunit-BS_DUNIT_B], unit_str_len) == 0) {
            pwr = (uint64_t) (dunit - BS_DUNIT_B);
            mpfr_pow_ui (dec_mul, dec_mul, pwr, MPFR_RNDN);
            mpfr_mul (size, size, dec_mul, MPFR_RNDN);
            mpfr_clear (dec_mul);
            return true;
        }

    /* not found among the binary and decimal units, let's try their translated
       verions */
    for (bunit=BS_BUNIT_B; bunit < BS_BUNIT_UNDEF; bunit++)
        if (strncasecmp (unit_str, b_units[bunit-BS_BUNIT_B], unit_str_len) == 0) {
            pwr = (uint64_t) bunit - BS_BUNIT_B;
            mpfr_mul_2exp (size, size, 10 * pwr, MPFR_RNDN);
            return true;
        }

    mpfr_init2 (dec_mul, BS_FLOAT_PREC_BITS);
    mpfr_set_ui (dec_mul, 1000, MPFR_RNDN);
    for (dunit=BS_DUNIT_B; dunit < BS_DUNIT_UNDEF; dunit++)
        if (strncasecmp (unit_str, d_units[dunit-BS_DUNIT_B], unit_str_len) == 0) {
            pwr = (uint64_t) (dunit - BS_DUNIT_B);
            mpfr_pow_ui (dec_mul, dec_mul, pwr, MPFR_RNDN);
            mpfr_mul (size, size, dec_mul, MPFR_RNDN);
            mpfr_clear (dec_mul);
            return true;
        }

    return false;
}

/**
 * set_error: (skip)
 *
 * Sets @error to @code and @msg (if not %NULL). **TAKES OVER @msg.**
 */
static void set_error (BSError **error, BSErrorCode code, char *msg) {
    *error = (BSError *) malloc (sizeof(BSError));
    (*error)->code = code;
    (*error)->msg = msg;
    return;
}

typedef void (*MpzOp) (mpz_t ROP, const mpz_t OP1, unsigned long int OP2);
static void do_64bit_add_sub (MpzOp op, mpz_t rop, const mpz_t op1, uint64_t op2) {
    uint64_t i = 0;
    uint64_t div = 0;
    uint64_t mod = 0;

    /* small enough to just work */
    if (op2 < (uint64_t) ULONG_MAX) {
        op (rop, op1, (unsigned long int) op2);
        return;
    }

    mpz_set (rop, op1);
    div = op2 / (uint64_t) ULONG_MAX;
    mod = op2 % (uint64_t) ULONG_MAX;
    for (i=0; i < div; i++)
        op (rop, rop, (unsigned long int) ULONG_MAX);
    op (rop, rop, (unsigned long int) mod);
}

static void mul_64bit (mpz_t rop, const mpz_t op1, uint64_t op2) {
    uint64_t i = 0;
    uint64_t div = 0;
    uint64_t mod = 0;
    mpz_t aux;
    mpz_t res;

    /* small enough to just work */
    if (op2 < (uint64_t) ULONG_MAX) {
        mpz_mul_ui (rop, op1, (unsigned long int) op2);
        return;
    }

    mpz_init2 (aux, (mp_bitcnt_t) 64);
    mpz_init2 (res, (mp_bitcnt_t) 64);

    mpz_set_ui (res, 0);
    div = op2 / (uint64_t) ULONG_MAX;
    mod = op2 % (uint64_t) ULONG_MAX;
    for (i=0; i < div; i++) {
        mpz_mul_ui (aux, op1, (unsigned long int) ULONG_MAX);
        mpz_add (res, res, aux);
    }
    mpz_mul_ui (aux, op1, (unsigned long int) mod);
    mpz_add (res, res, aux);

    mpz_set (rop, res);
    mpz_clear (aux);
    mpz_clear (res);
}



/***************
 * DESTRUCTORS *
 * *************/
/**
 * bs_size_free:
 *
 * Clears @size and frees the allocated resources.
 */
void bs_size_free (BSSize size) {
    mpz_clear (size->bytes);
    free (size);
}

/**
 * bs_clear_error:
 *
 * Clears @error and frees the allocated resources.
 */
void bs_clear_error (BSError **error) {
    if (error && *error) {
        free ((*error)->msg);
        free (*error);
        *error = NULL;
    }
    return;
}


/****************
 * CONSTRUCTORS *
 ****************/
/**
 * bs_size_new: (constructor)
 *
 * Creates a new #BSSize instance initialized to 0.
 *
 * Returns: a new #BSSize initialized to 0.
 */
BSSize bs_size_new (void) {
    BSSize ret = (BSSize) malloc (sizeof(struct _BSSize));
    bs_size_init (ret);
    return ret;
}

/**
 * bs_size_new_from_bytes: (constructor)
 * @bytes: number of bytes
 * @sgn: sign of the size -- if being -1, the size is initialized to
 *       -@bytes, other values are ignored
 *
 * Creates a new #BSSize instance.
 *
 * Returns: a new #BSSize
 */
BSSize bs_size_new_from_bytes (uint64_t bytes, int sgn) {
    char *num_str = NULL;
    BSSize ret = bs_size_new ();
    int ok = 0;

    ok = asprintf (&num_str, "%"PRIu64, bytes);
    if (ok == -1)
        /* probably cannot allocate memory, there's nothing more we can do */
        return ret;
    mpz_set_str (ret->bytes, num_str, 10);
    free (num_str);
    if (sgn == -1)
        mpz_neg (ret->bytes, ret->bytes);
    return ret;
}


/**
 * bs_size_new_from_str: (constructor)
 * @size_str: string representing the size as a number and an optional unit
 *            (e.g. "1 GiB")
 *
 * Creates a new #BSSize instance.
 *
 * Returns: a new #BSSize
 */
BSSize bs_size_new_from_str (const char *size_str, BSError **error) {
    char const * const pattern = "^\\s*         # white space \n" \
                                  "(?P<numeric>  # the numeric part consists of three parts, below \n" \
                                  " (-|\\+)?     # optional sign character \n" \
                                  " (?P<base>([0-9\\.%s]+))       # base \n" \
                                  " (?P<exp>(e|E)(-|\\+)[0-9]+)?) # exponent \n" \
                                  "\\s*               # white space \n" \
                                  "(?P<rest>[^\\s]*)\\s*$ # unit specification";
    char *real_pattern = NULL;
    pcre *regex = NULL;
    const char *error_msg = NULL;
    int erroffset;
    int str_len = 0;
    int ovector[30];            /* should be a multiple of 3 */
    int str_count = 0;
    char *num_str = NULL;
    const char *radix_char = NULL;
    char *loc_size_str = NULL;
    mpf_t parsed_size;
    mpfr_t size;
    int status = 0;
    char *unit_str = NULL;
    BSSize ret = NULL;

    radix_char = nl_langinfo (RADIXCHAR);
    if (strncmp (radix_char, ".", 1) != 0)
        real_pattern = strdup_printf (pattern, radix_char);
    else
        real_pattern = strdup_printf (pattern, "");

    regex = pcre_compile (real_pattern, PCRE_EXTENDED, &error_msg, &erroffset, NULL);
    free (real_pattern);
    if (!regex) {
        /* TODO: populate error */
        return NULL;
    }

    loc_size_str = replace_char_with_str (size_str, '.', radix_char);
    str_len = strlen (loc_size_str);

    str_count = pcre_exec (regex, NULL, loc_size_str, str_len,
                           0, 0, ovector, 30);
    if (str_count < 0) {
        set_error (error, BS_ERROR_INVALID_SPEC, strdup_printf ("Failed to parse size spec: %s", size_str));
        pcre_free (regex);
        free (loc_size_str);
        return NULL;
    }

    status = pcre_get_named_substring (regex, loc_size_str, ovector, str_count, "numeric", (const char **)&num_str);
    if (status < 0) {
        set_error (error, BS_ERROR_INVALID_SPEC, strdup_printf ("Failed to parse size spec: %s", size_str));
        pcre_free (regex);
        free (loc_size_str);
        return NULL;
    }

    /* parse the number using GMP because it knows how to handle localization
       much better than MPFR */
    mpf_init2 (parsed_size, BS_FLOAT_PREC_BITS);
    status = mpf_set_str (parsed_size, *num_str == '+' ? num_str+1 : num_str, 10);
    free (num_str);
    if (status != 0) {
        set_error (error, BS_ERROR_INVALID_SPEC, strdup_printf ("Failed to parse size spec: %s", size_str));
        pcre_free (regex);
        free (loc_size_str);
        mpf_clear (parsed_size);
        return NULL;
    }
    /* but use MPFR from now on because GMP thinks 0.1*1000 = 99 */
    mpfr_init2 (size, BS_FLOAT_PREC_BITS);
    mpfr_set_f (size, parsed_size, MPFR_RNDN);
    mpf_clear (parsed_size);

    status = pcre_get_named_substring (regex, loc_size_str, ovector, str_count, "rest", (const char **)&unit_str);
    if ((status >= 0) && strncmp (unit_str, "", 1) != 0) {
        strstrip (unit_str);
        if (!multiply_size_by_unit (size, unit_str)) {
            set_error (error, BS_ERROR_INVALID_SPEC, strdup_printf ("Failed to recognize unit from the spec: %s", size_str));
            free (unit_str);
            pcre_free (regex);
            free (loc_size_str);
            mpfr_clear (size);
            return NULL;
        }
    }
    free (unit_str);
    pcre_free (regex);

    ret = bs_size_new ();
    mpfr_get_z (ret->bytes, size, MPFR_RNDZ);

    free (loc_size_str);
    mpfr_clear (size);

    return ret;
}

/**
 * bs_size_new_from_size: (constructor)
 * @size: the size to create a new instance from (a copy of)
 *
 * Creates a new instance of #BSSize.
 *
 * Returns: (transfer full): a new #BSSize instance which is copy of @size.
 */
BSSize bs_size_new_from_size (const BSSize size) {
    BSSize ret = NULL;

    ret = bs_size_new ();
    mpz_set (ret->bytes, size->bytes);

    return ret;
}


/*****************
 * QUERY METHODS *
 *****************/
/**
 * bs_size_get_bytes:
 * @sgn: (allow-none) (out): sign of the @size - -1, 0 or 1 for negative, zero or positive
 *                           size respectively
 *
 * Get the number of bytes of the @size.
 *
 * Returns: the @size in a number of bytes
 */
uint64_t bs_size_get_bytes (const BSSize size, int *sgn, BSError **error) {
    char *num_str = NULL;
    mpz_t max;
    uint64_t ret = 0;
    int ok = 0;

    mpz_init2 (max, (mp_bitcnt_t) 64);
    ok = asprintf (&num_str, "%"PRIu64, UINT64_MAX);
    if (ok == -1) {
        /* we probably cannot allocate memory so we are doomed */
        set_error (error, BS_ERROR_FAIL, strdup("Failed to allocate memory"));
        mpz_clear (max);
        return 0;
    }
    mpz_set_str (max, num_str, 10);
    free (num_str);
    if (mpz_cmp (size->bytes, max) > 0) {
        set_error (error, BS_ERROR_OVER, strdup("The size is too big, cannot be returned as a 64bit number of bytes"));
        return 0;
    }
    mpz_clear (max);
    if (sgn)
        *sgn = mpz_sgn (size->bytes);
    if (mpz_cmp_ui (size->bytes, UINT64_MAX) <= 0)
        return (uint64_t) mpz_get_ui (size->bytes);
    else {
        num_str = bs_size_get_bytes_str (size);
        ret = strtoull (num_str, NULL, 10);
        free (num_str);
        return ret;
    }
}

/**
 * bs_size_sgn:
 *
 * Get the sign of the size.
 *
 * Returns: -1, 0 or 1 if @size is negative, zero or positive, respectively
 */
int bs_size_sgn (const BSSize size) {
    return mpz_sgn (size->bytes);
}

/**
 * bs_size_get_bytes_str:
 *
 * Get the number of bytes in @size as a string. This way, the caller doesn't
 * have to care about the limitations of some particular integer type.
 *
 * Returns: (transfer full): the string representing the @size as a number of bytes.
 */
char* bs_size_get_bytes_str (const BSSize size) {
    return mpz_get_str (NULL, 10, size->bytes);
}

/**
 * bs_size_convert_to:
 * @unit: the unit to convert @size to
 *
 * Get the @size converted to @unit as a string representing a floating-point
 * number.
 *
 * Returns: (transfer full): a string representing the floating-point number
 *                           that equals to @size converted to @unit
 */
char* bs_size_convert_to (const BSSize size, BSUnit unit, BSError **error) {
    BSBunit b_unit = BS_BUNIT_B;
    BSDunit d_unit = BS_DUNIT_B;
    mpf_t divisor;
    mpf_t result;
    bool found_match = false;
    char *ret = NULL;

    mpf_init2 (divisor, BS_FLOAT_PREC_BITS);
    for (b_unit = BS_BUNIT_B; !found_match && b_unit != BS_BUNIT_UNDEF; b_unit++) {
        if (unit.bunit == b_unit) {
            found_match = true;
            mpf_set_ui (divisor, 1);
            mpf_mul_2exp (divisor, divisor, 10 * (b_unit - BS_BUNIT_B));
        }
    }

    for (d_unit = BS_DUNIT_B; !found_match && d_unit != BS_DUNIT_UNDEF; d_unit++) {
        if (unit.dunit == d_unit) {
            found_match = true;
            mpf_set_ui (divisor, 1000);
            mpf_pow_ui (divisor, divisor, (d_unit - BS_DUNIT_B));
        }
    }

    if (!found_match) {
        set_error (error, BS_ERROR_INVALID_SPEC, "Invalid unit spec given");
        mpf_clear (divisor);
        return NULL;
    }

    mpf_init2 (result, BS_FLOAT_PREC_BITS);
    mpf_set_z (result, size->bytes);

    mpf_div (result, result, divisor);

    gmp_asprintf (&ret, "%.*Fg", BS_FLOAT_PREC_BITS/3, result);
    mpf_clears (divisor, result, NULL);

    return ret;
}

/**
 * bs_size_human_readable:
 * @min_unit: the smallest unit the returned representation should use
 * @max_places: maximum number of decimal places the representation should use
 * @xlate: whether to try to translate the representation or not
 *
 * Get a human-readable representation of @size.
 *
 * Returns: (transfer full): a string which is human-readable representation of
 *                           @size according to the restrictions given by the
 *                           other parameters
 */
char* bs_size_human_readable (const BSSize size, BSBunit min_unit, int max_places, bool xlate) {
    mpf_t cur_val;
    char *num_str = NULL;
    char *ret = NULL;
    int len = 0;
    char *zero = NULL;
    char *radix_char = NULL;
    int sign = 0;
    char *loc_num_str = NULL;
    bool at_radix = false;

    mpf_init2 (cur_val, BS_FLOAT_PREC_BITS);
    mpf_set_z (cur_val, size->bytes);

    if (min_unit == BS_BUNIT_UNDEF)
        min_unit = BS_BUNIT_B;

    sign = mpf_sgn (cur_val);
    mpf_abs (cur_val, cur_val);

    mpf_div_2exp (cur_val, cur_val, 10 * (min_unit - BS_BUNIT_B));
    while ((mpf_cmp_ui (cur_val, 1024) > 0) && min_unit != BS_BUNIT_YiB) {
        mpf_div_2exp (cur_val, cur_val, 10);
        min_unit++;
    }

    if (sign == -1)
        mpf_neg (cur_val, cur_val);

    len = gmp_asprintf (&num_str, "%.*Ff", max_places >= 0 ? max_places : BS_FLOAT_PREC_BITS,
                        cur_val);
    mpf_clear (cur_val);

    /* should use the proper radix char according to @xlate */
    radix_char = nl_langinfo (RADIXCHAR);
    if (!xlate) {
        loc_num_str = replace_str_with_str (num_str, radix_char, ".");
        free (num_str);
        radix_char = ".";
    } else
        loc_num_str = num_str;

    /* remove trailing zeros and the radix char */
    /* if max_places == 0, there can't be anything trailing */
    if (max_places != 0) {
        zero = loc_num_str + (len - 1);
        while ((zero != loc_num_str) && ((*zero == '0') || (*zero == *radix_char)) && !at_radix) {
            at_radix = *zero == *radix_char;
            zero--;
        }
        zero[1] = '\0';
    }

    ret = strdup_printf ("%s %s", loc_num_str, xlate ? _(b_units[min_unit - BS_BUNIT_B]) : b_units[min_unit - BS_BUNIT_B]);
    free (loc_num_str);

    return ret;
}


/***************
 * ARITHMETIC *
 ***************/
/**
 * bs_size_add:
 *
 * Add two sizes.
 *
 * Returns: (transfer full): a new instance of #BSSize which is a sum of @size1 and @size2
 */
BSSize bs_size_add (const BSSize size1, const BSSize size2) {
    BSSize ret = bs_size_new ();
    mpz_add (ret->bytes, size1->bytes, size2->bytes);

    return ret;
}

/**
 * bs_size_grow:
 *
 * Grows @size1 by @size2. IOW, adds @size2 to @size1 in-place (modifying
 * @size1).
 *
 * Basically an in-place variant of bs_size_add().
 *
 * Returns: (transfer none): @size1 modified by adding @size2 to it
 */
BSSize bs_size_grow (BSSize size1, const BSSize size2) {
    mpz_add (size1->bytes, size1->bytes, size2->bytes);

    return size1;
}

/**
 * bs_size_add_bytes:
 *
 * Add @bytes to the @size. To add a negative number of bytes use
 * bs_size_sub_bytes().
 *
 * Returns: (transfer full): a new instance of #BSSize which is a sum of @size and @bytes
 */
BSSize bs_size_add_bytes (const BSSize size, uint64_t bytes) {
    BSSize ret = bs_size_new ();
    do_64bit_add_sub (mpz_add_ui, ret->bytes, size->bytes, bytes);

    return ret;
}

/**
 * bs_size_grow_bytes:
 *
 * Grows @size by @bytes. IOW, adds @bytes to @size in-place (modifying @size).
 *
 * Basically an in-place variant of bs_size_add_bytes().
 *
 * Returns: (transfer none): @size modified by adding @bytes to it
 */
BSSize bs_size_grow_bytes (BSSize size, const uint64_t bytes) {
    do_64bit_add_sub (mpz_add_ui, size->bytes, size->bytes, bytes);

    return size;
}

/**
 * bs_size_sub:
 *
 * Subtract @size2 from @size1.
 *
 * Returns: (transfer full): a new instance of #BSSize which is equals to @size1 - @size2
 */
BSSize bs_size_sub (const BSSize size1, const BSSize size2) {
    BSSize ret = bs_size_new ();
    mpz_sub (ret->bytes, size1->bytes, size2->bytes);

    return ret;
}

/**
 * bs_size_shrink:
 *
 * Shrinks @size1 by @size2. IOW, subtracts @size2 from @size1 in-place
 * (modifying @size1).
 *
 * Basically an in-place variant of bs_size_sub().
 *
 * Returns: (transfer none): @size1 modified by subtracting @size2 from it
 */
BSSize bs_size_shrink (BSSize size1, const BSSize size2) {
    mpz_sub (size1->bytes, size1->bytes, size2->bytes);

    return size1;
}

/**
 * bs_size_sub_bytes:
 *
 * Subtract @bytes from the @size. To subtract a negative number of bytes use
 * bs_size_add_bytes().
 *
 * Returns: (transfer full): a new instance of #BSSize which equals to @size - @bytes
 */
BSSize bs_size_sub_bytes (const BSSize size, uint64_t bytes) {
    BSSize ret = bs_size_new ();
    do_64bit_add_sub (mpz_sub_ui, ret->bytes, size->bytes, bytes);

    return ret;
}

/**
 * bs_size_shrink_bytes:
 *
 * Shrinks @size by @bytes. IOW, subtracts @bytes from @size in-place
 * (modifying @size). To shrink by a negative number of bytes use
 * bs_size_grow_bytes().
 *
 * Basically an in-place variant of bs_size_sub_bytes().
 *
 * Returns: (transfer none): @size modified by subtracting @bytes from it
 */
BSSize bs_size_shrink_bytes (BSSize size, uint64_t bytes) {
    do_64bit_add_sub (mpz_sub_ui, size->bytes, size->bytes, bytes);

    return size;
}

/**
 * bs_size_mul_int:
 *
 * Multiply @size by @times.
 *
 * Returns: (transfer full): a new instance of #BSSize which equals to @size * @times
 */
BSSize bs_size_mul_int (const BSSize size, uint64_t times) {
    BSSize ret = bs_size_new ();
    mul_64bit (ret->bytes, size->bytes, times);

    return ret;
}

/**
 * bs_size_grow_mul_int:
 *
 * Grow @size @times times. IOW, multiply @size by @times in-place.
 *
 * Basically an in-place variant of bs_size_mul_int().
 *
 * Returns: (transfer none): @size modified by growing it @times times
 */
BSSize bs_size_grow_mul_int (BSSize size, uint64_t times) {
    mul_64bit (size->bytes, size->bytes, times);

    return size;
}

/**
 * bs_size_mul_float_str:
 *
 * Multiply @size by the floating-point number @float_str represents.
 *
 * Returns: (transfer full): a new #BSSize instance which equals to
 *                           @size * @times_str
 *
 */
BSSize bs_size_mul_float_str (const BSSize size, const char *float_str, BSError **error) {
    mpf_t op1, op2;
    int status = 0;
    BSSize ret = NULL;
    const char *radix_char = NULL;
    char *loc_float_str = NULL;

    radix_char = nl_langinfo (RADIXCHAR);

    mpf_init2 (op1, BS_FLOAT_PREC_BITS);
    mpf_init2 (op2, BS_FLOAT_PREC_BITS);

    mpf_set_z (op1, size->bytes);
    loc_float_str = replace_char_with_str (float_str, '.', radix_char);
    status = mpf_set_str (op2, loc_float_str, 10);
    if (status != 0) {
        set_error (error, BS_ERROR_INVALID_SPEC, strdup_printf ("'%s' is not a valid floating point number string", loc_float_str));
        free (loc_float_str);
        mpf_clears (op1, op2, NULL);
        return NULL;
    }
    free (loc_float_str);

    mpf_mul (op1, op1, op2);

    ret = bs_size_new ();
    mpz_set_f (ret->bytes, op1);
    mpf_clears (op1, op2, NULL);

    return ret;
}

/**
 * bs_size_grow_mul_float_str:
 *
 * Grow @size by the floating-point number @float_str represents times. IOW,
 * multiply @size by @float_str in-place.
 *
 * Basically an in-place variant of bs_size_grow_mul_float_str().
 *
 * Returns: (transfer none): @size modified by growing it @float_str times.
 */
BSSize bs_size_grow_mul_float_str (BSSize size, const char *float_str, BSError **error) {
    mpf_t op1, op2;
    int status = 0;
    const char *radix_char = NULL;
    char *loc_float_str = NULL;

    radix_char = nl_langinfo (RADIXCHAR);

    mpf_init2 (op1, BS_FLOAT_PREC_BITS);
    mpf_init2 (op2, BS_FLOAT_PREC_BITS);

    mpf_set_z (op1, size->bytes);
    loc_float_str = replace_char_with_str (float_str, '.', radix_char);
    status = mpf_set_str (op2, loc_float_str, 10);
    if (status != 0) {
        set_error (error, BS_ERROR_INVALID_SPEC, strdup_printf ("'%s' is not a valid floating point number string", loc_float_str));
        free (loc_float_str);
        mpf_clears (op1, op2, NULL);
        return NULL;
    }
    free (loc_float_str);

    mpf_mul (op1, op1, op2);

    mpz_set_f (size->bytes, op1);
    mpf_clears (op1, op2, NULL);

    return size;
}

/**
 * bs_size_div:
 * @sgn: (allow-none) (out): sign of the result
 *
 * Divide @size1 by @size2. Gives the answer to the question "How many times
 * does @size2 fit in @size1?".
 *
 * Returns: integer number x so that x * @size1 < @size2 and (x+1) * @size1 > @size2
 *          (IOW, @size1 / @size2 using integer division)
 */
uint64_t bs_size_div (const BSSize size1, const BSSize size2, int *sgn, BSError **error) {
    mpz_t result;
    uint64_t ret = 0;

    if (mpz_cmp_ui (size2->bytes, 0) == 0) {
        set_error (error, BS_ERROR_ZERO_DIV, strdup_printf ("Division by zero"));
        return 0;
    }

    if (sgn)
        *sgn = mpz_sgn (size1->bytes) * mpz_sgn (size2->bytes);
    mpz_init (result);
    mpz_tdiv_q (result, size1->bytes, size2->bytes);

    if (mpz_cmp_ui (result, UINT64_MAX) > 0) {
        set_error (error, BS_ERROR_OVER, strdup_printf ("The size is too big, cannot be returned as a 64bit number"));
        mpz_clear (result);
        return 0;
    }
    ret = (uint64_t) mpz_get_ui (result);

    mpz_clear (result);
    return ret;
}

/**
 * bs_size_div_int:
 *
 * Divide @size by @divisor. Gives the answer to the question "What is the size
 * of each chunk if @size is split into a @divisor number of pieces?"
 *
 * Note: Due to the limitations of the current implementation the maximum value
 * @divisor is ULONG_MAX (which can differ from UINT64_MAX). An error
 * (BS_ERROR_OVER) is returned if overflow happens.
 *
 * Returns: (transfer full): a #BSSize instance x so that x * @divisor = @size,
 *                           rounded to a number of bytes
 */
BSSize bs_size_div_int (const BSSize size, uint64_t divisor, BSError **error) {
    BSSize ret = NULL;

    if (divisor == 0) {
        set_error (error, BS_ERROR_ZERO_DIV, strdup_printf ("Division by zero"));
        return NULL;
    } else if (divisor > ULONG_MAX) {
        set_error (error, BS_ERROR_OVER, strdup_printf ("Divisor too big, must be less or equal to %lu", ULONG_MAX));
        return NULL;
    }
    ret = bs_size_new ();
    mpz_tdiv_q_ui (ret->bytes, size->bytes, divisor);

    return ret;
}

/**
 * bs_size_shrink_div_int:
 *
 * Shrink @size by dividing by @divisor. IOW, divide @size by @divisor in-place.
 *
 * Basically an in-place variant of bs_size_div_int().
 *
 * Note: Due to the limitations of the current implementation the maximum value
 * @divisor is ULONG_MAX (which can differ from UINT64_MAX). An error
 * (BS_ERROR_OVER) is returned if overflow happens.
 *
 * Returns: (transfer none): @size modified by division by @divisor
 */
BSSize bs_size_shrink_div_int (BSSize size, uint64_t divisor, BSError **error) {
    if (divisor == 0) {
        set_error (error, BS_ERROR_ZERO_DIV, strdup_printf ("Division by zero"));
        return NULL;
    } else if (divisor > ULONG_MAX) {
        set_error (error, BS_ERROR_OVER, strdup_printf ("Divisor too big, must be less or equal to %lu", ULONG_MAX));
        return NULL;
    }

    mpz_tdiv_q_ui (size->bytes, size->bytes, divisor);

    return size;
}

/**
 * bs_size_true_div:
 *
 * Divides @size1 by @size2.
 *
 * Returns: (transfer full): a string representing the floating-point number
 *                           that equals to @size1 / @size2
 */
char* bs_size_true_div (const BSSize size1, const BSSize size2, BSError **error) {
    mpf_t op1;
    mpf_t op2;
    char *ret = NULL;

    if (mpz_cmp_ui (size2->bytes, 0) == 0) {
        set_error (error, BS_ERROR_ZERO_DIV, strdup_printf("Division by zero"));
        return 0;
    }

    mpf_init2 (op1, BS_FLOAT_PREC_BITS);
    mpf_init2 (op2, BS_FLOAT_PREC_BITS);
    mpf_set_z (op1, size1->bytes);
    mpf_set_z (op2, size2->bytes);

    mpf_div (op1, op1, op2);

    gmp_asprintf (&ret, "%.*Fg", BS_FLOAT_PREC_BITS/3, op1);

    mpf_clears (op1, op2, NULL);

    return ret;
}

/**
 * bs_size_true_div_int:
 *
 * Divides @size by @divisor.
 *
 * Note: Due to the limitations of the current implementation the maximum value
 * @divisor is ULONG_MAX (which can differ from UINT64_MAX). An error
 * (BS_ERROR_OVER) is returned if overflow happens.
 *
 * Returns: (transfer full): a string representing the floating-point number
 *                           that equals to @size / @divisor
 */
char* bs_size_true_div_int (const BSSize size, uint64_t divisor, BSError **error) {
    mpf_t op1;
    char *ret = NULL;

    if (divisor == 0) {
        set_error (error, BS_ERROR_ZERO_DIV, strdup_printf ("Division by zero"));
        return 0;
    } else if (divisor > ULONG_MAX) {
        set_error (error, BS_ERROR_OVER, strdup_printf ("Divisor too big, must be less or equal to %lu", ULONG_MAX));
        return NULL;
    }

    mpf_init2 (op1, BS_FLOAT_PREC_BITS);
    mpf_set_z (op1, size->bytes);

    mpf_div_ui (op1, op1, divisor);

    gmp_asprintf (&ret, "%.*Fg", BS_FLOAT_PREC_BITS/3, op1);

    mpf_clear (op1);

    return ret;
}

/**
 * bs_size_mod:
 *
 * Gives @size1 modulo @size2 (i.e. the remainder of integer division @size1 /
 * @size2). Gives the answer to the question "If I split @size1 into chunks of
 * size @size2, what will be the remainder?"
 * **This function ignores the signs of the sizes.**
 *
 * Returns: (transfer full): a #BSSize instance that is a remainder of
 *                           @size1 / @size2 using integer division
 */
BSSize bs_size_mod (const BSSize size1, const BSSize size2, BSError **error) {
    mpz_t aux;
    BSSize ret = NULL;
    if (mpz_cmp_ui (size2->bytes, 0) == 0) {
        set_error (error, BS_ERROR_ZERO_DIV, strdup_printf ("Division by zero"));
        return 0;
    }

    mpz_init (aux);
    mpz_set (aux, size1->bytes);
    if (mpz_sgn (size1->bytes) == -1)
        /* negative @size1, get the absolute value so that we get results
           matching the specification/documentation of this function */
        mpz_neg (aux, aux);

    ret = bs_size_new ();
    mpz_mod (ret->bytes, aux, size2->bytes);

    return ret;
}

/**
 * bs_size_round_to_nearest:
 * @round_to: to a multiple of what to round @size
 * @dir: %BS_ROUND_DIR_UP to round up (to the nearest multiple of @round_to
 *       bigger than @size) or %BS_ROUND_DIR_DOWN to round down (to the
 *       nearest multiple of @round_to smaller than @size)
 *
 * Round @size to the nearest multiple of @round_to according to the direction
 * given by @dir.
 *
 * Returns: (transfer full): a new instance of #BSSize that is @size rounded to
 *                           a multiple of @round_to according to @dir
 */
BSSize bs_size_round_to_nearest (const BSSize size, const BSSize round_to, BSRoundDir dir, BSError **error) {
    BSSize ret = NULL;
    mpz_t q;
    mpz_t aux_size;

    if (mpz_cmp_ui (round_to->bytes, 0) == 0) {
        set_error (error, BS_ERROR_ZERO_DIV, strdup_printf ("Division by zero"));
        return NULL;
    }

    mpz_init (q);

    if (dir == BS_ROUND_DIR_UP) {
        mpz_cdiv_q (q, size->bytes, round_to->bytes);
    } else if (dir == BS_ROUND_DIR_HALF_UP) {
        /* round half up == add half of what to round to and round down */
        mpz_init (aux_size);
        mpz_fdiv_q_ui (aux_size, round_to->bytes, 2);
        mpz_add (aux_size, aux_size, size->bytes);
        mpz_fdiv_q (q, aux_size, round_to->bytes);
        mpz_clear (aux_size);
    } else
        mpz_fdiv_q (q, size->bytes, round_to->bytes);

    ret = bs_size_new ();
    mpz_mul (ret->bytes, q, round_to->bytes);

    mpz_clear (q);

    return ret;
}


/***************
 * COMPARISONS *
 ***************/
/**
 * bs_size_cmp:
 * @abs: whether to compare absolute values of @size1 and @size2 instead
 *
 * Compare @size1 and @size2. This function behaves like the standard *cmp*()
 * functions.
 *
 * Returns: -1, 0, or 1 if @size1 is smaller, equal to or bigger than
 *          @size2 respectively comparing absolute values if @abs is %true
 */
int bs_size_cmp (const BSSize size1, const BSSize size2, bool abs) {
    int ret = 0;
    if (abs)
        ret = mpz_cmpabs (size1->bytes, size2->bytes);
    else
        ret = mpz_cmp (size1->bytes, size2->bytes);
    /* make sure we don't return things like 2 or -2 (which GMP can give us) */
    if (ret > 0)
        ret = 1;
    else if (ret < 0)
        ret = -1;
    return ret;
}

/**
 * bs_size_cmp_bytes:
 * @abs: whether to compare absolute values of @size and @bytes instead.
 *
 * Compare @size and @bytes, i.e. the number of bytes @size has with
 * @bytes. This function behaves like the standard *cmp*() functions.
 *
 * Returns: -1, 0, or 1 if @size is smaller, equal to or bigger than
 *          @bytes respectively comparing absolute values if @abs is %true
 */
int bs_size_cmp_bytes (const BSSize size, uint64_t bytes, bool abs) {
    int ret = 0;
    if (abs)
        ret = mpz_cmpabs_ui (size->bytes, bytes);
    else
        ret = mpz_cmp_ui (size->bytes, bytes);
    /* make sure we don't return things like 2 or -2 (which GMP can give us) */
    if (ret > 0)
        ret = 1;
    else if (ret < 0)
        ret = -1;
    return ret;
}
