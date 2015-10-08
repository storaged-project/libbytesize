#include <glib.h>
#include <glib-object.h>
#include <gmp.h>
#include <langinfo.h>

#include "bs_size.h"
#include "gettext.h"

#define  _(String) gettext (String)
#define N_(String) String

/**
 * SECTION: Size
 * @title: BSSize
 * @short_description: a class facilitating work with sizes in bytes
 *
 * A #BSSize is class that facilitates work with sizes in bytes by providing
 * functions/methods that are required for parsing users input when entering
 * size, showing size in nice human-readable format, storing sizes bigger than
 * %G_MAXUINT64 and doing calculations with sizes without loss of
 * precision/information.
 */

/* static void* realloc_old_new (void *ptr, gsize old_size __attribute__ ((unused)), gsize new_size) { */
/*     return g_try_realloc (ptr, new_size); */
/* } */

/* static void free_old (void *ptr, gsize old_size __attribute__ ((unused))) { */
/*     return g_free (ptr); */
/* } */

/* static void init (void) { */
/*     mp_set_memory_functions (g_try_malloc, realloc_old_new, free_old); */
/* } */


/***************
 * STATIC DATA *
 ***************/
static gchar const * const b_units[BS_BUNIT_UNDEF] = {N_("B"), N_("KiB"), N_("MiB"), N_("GiB"), N_("TiB"),
                                                      N_("PiB"), N_("EiB"), N_("ZiB"), N_("YiB")};

static gchar const * const d_units[BS_DUNIT_UNDEF] = {N_("B"), N_("KB"), N_("MB"), N_("GB"), N_("TB"),
                                                      N_("PB"), N_("EB"), N_("ZB"), N_("YB")};


/****************************
 * CLASS/OBJECT DEFINITIONS *
 ****************************/
/**
 * BSSize:
 *
 * The BSSize struct contains only private fields and should not be directly
 * accessed.
 */
struct _BSSize {
    GObject parent;
    BSSizePrivate *priv;
};

/**
 * BSSizeClass:
 * @parent_class: parent class of the #BSSizeClass
 */
struct _BSSizeClass {
    GObjectClass parent_class;
};

/**
 * BSSizePrivate:
 *
 * The BSSizePrivate struct contains only private fields and should not be directly
 * accessed.
 */
struct _BSSizePrivate {
    mpz_t bytes;
};

GQuark bs_size_error_quark (void)
{
    return g_quark_from_static_string ("g-bs-size-error-quark");
}

G_DEFINE_TYPE (BSSize, bs_size, G_TYPE_OBJECT)

static void bs_size_dispose(GObject *size);

static void bs_size_class_init (BSSizeClass *klass) {
    GObjectClass *object_class = G_OBJECT_CLASS(klass);

    object_class->dispose = bs_size_dispose;

    g_type_class_add_private(object_class, sizeof(BSSizePrivate));
}

static void bs_size_init (BSSize *self) {
    self->priv = G_TYPE_INSTANCE_GET_PRIVATE(self,
                                             BS_TYPE_SIZE,
                                             BSSizePrivate);
    /* let's start with 64 bits of space */
    mpz_init2 (self->priv->bytes, (mp_bitcnt_t) 64);
}

static void bs_size_dispose (GObject *object) {
    BSSize *self = BS_SIZE (object);
    mpz_clear (self->priv->bytes);

    G_OBJECT_CLASS(bs_size_parent_class)->dispose (object);
}


/****************
 * CONSTRUCTORS *
 ****************/
/**
 * bs_size_new: (constructor)
 * Creates a new #BSSize instance.
 *
 * Returns: a new #BSSize
 */
BSSize* bs_size_new (void) {
    return BS_SIZE (g_object_new (BS_TYPE_SIZE, NULL));
}

/**
 * bs_size_new_from_bytes: (constructor)
 *
 * Creates a new #BSSize instance.
 *
 * Returns: a new #BSSize
 */
BSSize* bs_size_new_from_bytes (guint64 bytes, gint sgn, GError **error __attribute__((unused))) {
    BSSize *ret = bs_size_new ();
    mpz_set_ui (ret->priv->bytes, bytes);
    if (sgn == -1)
        mpz_neg (ret->priv->bytes, ret->priv->bytes);
    return ret;
}

/**
 * replace_char:
 *
 * Replaces all appereances of @orig in @str with @new (in place).
 */
static gchar *replace_char (gchar *str, gchar orig, gchar new) {
    gchar *pos = str;
    if (!str)
        return str;

    for (pos=str; pos; pos++)
        *pos = *pos == orig ? new : *pos;

    return str;
}

static gboolean multiply_size_by_unit (mpf_t size, gchar *unit_str) {
    BSBunit bunit = BS_BUNIT_UNDEF;
    BSDunit dunit = BS_DUNIT_UNDEF;
    guint64 pwr = 0;
    mpf_t dec_mul;
    gsize unit_str_len = 0;

    unit_str_len = strlen (unit_str);

    for (bunit=BS_BUNIT_B; bunit < BS_BUNIT_UNDEF; bunit++)
        if (g_ascii_strncasecmp (unit_str, b_units[bunit-BS_BUNIT_B], unit_str_len) == 0) {
            pwr = (guint64) bunit - BS_BUNIT_B;
            mpf_mul_2exp (size, size, 10 * pwr);
            return TRUE;
        }

    mpf_init2 (dec_mul, BS_FLOAT_PREC_BITS);
    mpf_set_ui (dec_mul, 1000);
    for (dunit=BS_DUNIT_B; dunit < BS_DUNIT_UNDEF; dunit++)
        if (g_ascii_strncasecmp (unit_str, d_units[dunit-BS_DUNIT_B], unit_str_len) == 0) {
            pwr = (guint64) (dunit - BS_DUNIT_B);
            mpf_pow_ui (dec_mul, dec_mul, pwr);
            mpf_mul (size, size, dec_mul);
            mpf_clear (dec_mul);
            return TRUE;
        }

    /* not found among the binary and decimal units, let's try their translated
       verions */
    for (bunit=BS_BUNIT_B; bunit < BS_BUNIT_UNDEF; bunit++)
        if (g_ascii_strncasecmp (unit_str, b_units[bunit-BS_BUNIT_B], unit_str_len) == 0) {
            pwr = (guint64) bunit - BS_BUNIT_B;
            mpf_mul_2exp (size, size, 10 * pwr);
            return TRUE;
        }

    mpf_init2 (dec_mul, BS_FLOAT_PREC_BITS);
    mpf_set_ui (dec_mul, 1000);
    for (dunit=BS_DUNIT_B; dunit < BS_DUNIT_UNDEF; dunit++)
        if (g_ascii_strncasecmp (unit_str, d_units[dunit-BS_DUNIT_B], unit_str_len) == 0) {
            pwr = (guint64) (dunit - BS_DUNIT_B);
            mpf_pow_ui (dec_mul, dec_mul, pwr);
            mpf_mul (size, size, dec_mul);
            mpf_clear (dec_mul);
            return TRUE;
        }

    return FALSE;
}


/**
 * bs_size_new_from_str: (constructor)
 *
 * Creates a new #BSSize instance.
 *
 * Returns: a new #BSSize
 */
BSSize* bs_size_new_from_str (const gchar *size_str, GError **error) {
    gchar const * const pattern = "(?P<numeric>  # the numeric part consists of three parts, below \n" \
                                  " (-|\\+)?     # optional sign character \n" \
                                  " (?P<base>([0-9\\.]+))         # base \n" \
                                  " (?P<exp>(e|E)(-|\\+)[0-9]+)?) # exponent \n" \
                                  "\\s*               # white space \n" \
                                  "(?P<rest>[^\\s]*$) # unit specification";
    GRegex *regex = NULL;
    gboolean success = FALSE;
    GMatchInfo *match_info = NULL;
    gchar *num_str = NULL;
    gchar *radix_char = NULL;
    gchar *loc_size_str = g_strdup (size_str);
    mpf_t size;
    gint status = 0;
    gchar *unit_str = NULL;
    BSSize *ret = NULL;

    radix_char = nl_langinfo (RADIXCHAR);
    if (g_strcmp0 (radix_char, ".") != 0)
        replace_char (loc_size_str, '.', *radix_char);

    regex = g_regex_new (pattern, G_REGEX_EXTENDED, 0, error);
    if (!regex) {
        g_free (loc_size_str);
        /* error is already populated */
        return NULL;
    }

    success = g_regex_match (regex, loc_size_str, 0, &match_info);
    if (!success) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_INVALID_SPEC,
                     "Failed to parse size spec: %s", size_str);
        g_regex_unref (regex);
        g_match_info_free (match_info);
        g_free (loc_size_str);
        return NULL;
    }
    g_regex_unref (regex);

    num_str = g_match_info_fetch_named (match_info, "numeric");
    if (!num_str) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_INVALID_SPEC,
                     "Failed to parse size spec: %s", size_str);
        g_regex_unref (regex);
        g_match_info_free (match_info);
        g_free (loc_size_str);
        return NULL;
    }

    mpf_init2 (size, BS_FLOAT_PREC_BITS);
    status = mpf_set_str (size, num_str, 10);
    if (status != 0) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_INVALID_SPEC,
                     "Failed to parse size spec: %s", size_str);
        g_match_info_free (match_info);
        g_free (loc_size_str);
        mpf_clear (size);
        return NULL;
    }

    unit_str = g_match_info_fetch_named (match_info, "rest");
    if (unit_str && g_strcmp0 (unit_str, "") != 0) {
        g_strstrip (unit_str);
        if (!multiply_size_by_unit (size, unit_str)) {
            g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_INVALID_SPEC,
                         "Failed to recognize unit from the spec: %s", size_str);
            g_match_info_free (match_info);
            g_free (loc_size_str);
            mpf_clear (size);
            return NULL;
        }
    }

    ret = bs_size_new ();
    mpz_set_f (ret->priv->bytes, size);

    g_free (loc_size_str);
    g_match_info_free (match_info);
    mpf_clear (size);

    return ret;
}

/**
 * bs_size_new_from_size: (constructor)
 *
 * Returns: (transfer full): a new #BSSize instance which is copy of @size.
 */
BSSize* bs_size_new_from_size (BSSize *size, GError **error __attribute__((unused))) {
    BSSize *ret = NULL;

    ret = bs_size_new ();
    mpz_set (ret->priv->bytes, size->priv->bytes);

    return ret;
}


/*****************
 * QUERY METHODS *
 *****************/
/**
 * bs_size_get_bytes:
 * @sgn: (out): sign of the @size
 *
 * Returns: the @size in a number of bytes
 */
guint64 bs_size_get_bytes (BSSize *size, gint *sgn, GError **error) {
    if (mpz_cmp_ui (size->priv->bytes, G_MAXUINT64) > 0) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_OVER,
                     "The size is too big, cannot be returned as a 64bit number of bytes");
        return 0;
    }
    *sgn = mpz_sgn (size->priv->bytes);
    return (guint64) mpz_get_ui (size->priv->bytes);
}

/**
 * bs_size_sgn:
 *
 * Returns: -1, 0 or 1 if @size is negative, zero or positive, respectively
 */
gint bs_size_sgn (BSSize *size) {
    return mpz_sgn (size->priv->bytes);
}

/**
 * bs_size_get_bytes_str:
 *
 * Returns: (transfer full): the string representing the @size as a number of bytes.
 */
gchar* bs_size_get_bytes_str (BSSize *size, GError **error __attribute__((unused))) {
    return mpz_get_str (NULL, 10, size->priv->bytes);
}

/**
 * bs_size_convert_to:
 *
 * Returns: (transfer full): a string representing the floating-point number
 *                           that equals to @size converted to @unit
 */
gchar* bs_size_convert_to (BSSize *size, BSUnit unit, GError **error) {
    BSBunit b_unit = BS_BUNIT_B;
    BSDunit d_unit = BS_DUNIT_B;
    mpf_t divisor;
    mpf_t result;
    gboolean found_match = FALSE;
    gchar *ret = NULL;

    mpf_init2 (divisor, BS_FLOAT_PREC_BITS);
    for (b_unit = BS_BUNIT_B; !found_match && b_unit != BS_BUNIT_UNDEF; b_unit++) {
        if (unit.bunit == b_unit) {
            found_match = TRUE;
            mpf_set_ui (divisor, 1);
            mpf_mul_2exp (divisor, divisor, 10 * (b_unit - BS_BUNIT_B));
        }
    }

    for (d_unit = BS_DUNIT_B; !found_match && d_unit != BS_DUNIT_UNDEF; d_unit++) {
        if (unit.dunit == d_unit) {
            found_match = TRUE;
            mpf_set_ui (divisor, 1000);
            mpf_pow_ui (divisor, divisor, (d_unit - BS_DUNIT_B));
        }
    }

    if (!found_match) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_INVALID_SPEC,
                     "Invalid unit spec given");
        mpf_clear (divisor);
        return NULL;
    }

    mpf_init2 (result, BS_FLOAT_PREC_BITS);
    mpf_set_z (result, size->priv->bytes);

    mpf_div (result, result, divisor);

    gmp_asprintf (&ret, "%.*Fg", BS_FLOAT_PREC_BITS/3, result);
    mpf_clears (divisor, result, NULL);

    return ret;
}

/**
 * bs_size_human_readable:
 *
 * Returns: (transfer full): a string which is human-readable representation of
 *                           @size according to the restrictions given by the
 *                           other parameters
 */
gchar* bs_size_human_readable (BSSize *size, BSBunit min_unit, gint max_places, gboolean xlate) {
    mpf_t cur_val;
    gchar *num_str = NULL;
    gchar *ret = NULL;
    gint len = 0;
    gchar *zero = NULL;
    gchar *radix_char = NULL;
    gint sign = 0;

    mpf_init2 (cur_val, BS_FLOAT_PREC_BITS);
    mpf_set_z (cur_val, size->priv->bytes);

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

    /* remove trailing zeros and the radix char */
    radix_char = nl_langinfo (RADIXCHAR);
    zero = num_str + (len - 1);
    while ((zero != num_str) && ((*zero == '0') || (*zero == *radix_char)))
        zero--;
    zero[1] = '\0';

    ret = g_strdup_printf ("%s %s", num_str, xlate ? _(b_units[min_unit - BS_BUNIT_B]) : b_units[min_unit - BS_BUNIT_B]);
    g_free (num_str);

    return ret;
}


/***************
 * ARITHMETIC *
 ***************/
/**
 * bs_size_add:
 *
 * Returns: (transfer full): a new instance of #BSSize which is a sum of @size1 and @size2
 */
BSSize* bs_size_add (BSSize *size1, BSSize *size2) {
    BSSize *ret = bs_size_new ();
    mpz_add (ret->priv->bytes, size1->priv->bytes, size2->priv->bytes);

    return ret;
}

/**
 * bs_size_add_bytes:
 *
 * Returns: (transfer full): a new instance of #BSSize which is a sum of @size and @bytes
 */
BSSize* bs_size_add_bytes (BSSize *size, guint64 bytes) {
    BSSize *ret = bs_size_new ();
    mpz_add_ui (ret->priv->bytes, size->priv->bytes, bytes);

    return ret;
}

/**
 * bs_size_sub:
 *
 * Returns: (transfer full): a new instance of #BSSize which is equals to @size1 - @size2
 */
BSSize* bs_size_sub (BSSize *size1, BSSize *size2) {
    BSSize *ret = bs_size_new ();
    mpz_sub (ret->priv->bytes, size1->priv->bytes, size2->priv->bytes);

    return ret;
}

/**
 * bs_size_sub_bytes:
 *
 * Returns: (transfer full): a new instance of #BSSize which is equals to @size - @bytes
 */
BSSize* bs_size_sub_bytes (BSSize *size, guint64 bytes) {
    BSSize *ret = bs_size_new ();
    mpz_sub_ui (ret->priv->bytes, size->priv->bytes, bytes);

    return ret;
}

/**
 * bs_size_mul_int:
 *
 * Returns: (transfer full): a new instance of #BSSize which is equals to @size * @times
 */
BSSize* bs_size_mul_int (BSSize *size, guint64 times) {
    BSSize *ret = bs_size_new ();
    mpz_mul_ui (ret->priv->bytes, size->priv->bytes, times);

    return ret;
}

/**
 * bs_size_mul_float_str:
 *
 * Returns: (transfer full): a new #BSSize instance which equals to @size *
 * @times_str
 *
 * The reason why this function takes a float as a string instead of a float
 * directly is because a string "0.3" can be translated into 0.3 with
 * appropriate precision while 0.3 as float is probably something like
 * 0.294343... with unknown precision.
 */
BSSize* bs_size_mul_float_str (BSSize *size, const gchar *float_str, GError **error) {
    mpf_t op1, op2;
    gint status = 0;
    BSSize *ret = NULL;

    mpf_init2 (op1, BS_FLOAT_PREC_BITS);
    mpf_init2 (op2, BS_FLOAT_PREC_BITS);

    mpf_set_z (op1, size->priv->bytes);
    status = mpf_set_str (op2, float_str, 10);
    if (status != 0) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_INVALID_SPEC,
                     "'%s' is not a valid floating point number string", float_str);
        mpf_clears (op1, op2, NULL);
        return NULL;
    }

    mpf_mul (op1, op1, op2);

    ret = bs_size_new ();
    mpz_set_f (ret->priv->bytes, op1);
    mpf_clears (op1, op2, NULL);

    return ret;
}

/**
 * bs_size_div:
 *
 * Returns: integer number x so that x * @size1 < @size2 and (x+1) * @size1 > @size2
 *          (IOW, @size1 / @size2 using integer division)
 */
guint64 bs_size_div (BSSize *size1, BSSize *size2, GError **error) {
    mpz_t result;
    guint64 ret = 0;

    if (mpz_cmp_ui (size2->priv->bytes, 0) == 0) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_ZERO_DIV,
                     "Division by zero");
        return 0;
    }

    mpz_init (result);
    mpz_fdiv_q (result, size1->priv->bytes, size2->priv->bytes);

    if (mpz_cmp_ui (result, G_MAXUINT64) > 0) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_OVER,
                     "The size is too big, cannot be returned as a 64bit number of bytes");
        mpz_clear (result);
        return 0;
    }
    ret = (guint64) mpz_get_ui (result);

    mpz_clear (result);
    return ret;
}

/**
 * bs_size_div_int:
 *
 * Returns: (transfer full): a #BSSize instance x so that x * @divisor = @size,
 *                           rounded to a number of bytes
 */
BSSize* bs_size_div_int (BSSize *size, guint64 divisor, GError **error) {
    BSSize *ret = NULL;

    if (divisor == 0) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_ZERO_DIV,
                     "Division by zero");
        return NULL;
    }

    ret = bs_size_new ();
    mpz_fdiv_q_ui (ret->priv->bytes, size->priv->bytes, divisor);

    return ret;
}

/**
 * bs_size_true_div:
 *
 * Returns: (transfer full): a string representing the floating-point number
 *                           that equals to @size1 / @size2
 */
gchar* bs_size_true_div (BSSize *size1, BSSize *size2, GError **error) {
    mpf_t op1;
    mpf_t op2;
    gchar *ret = NULL;

    if (mpz_cmp_ui (size2->priv->bytes, 0) == 0) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_ZERO_DIV,
                     "Division by zero");
        return 0;
    }

    mpf_init2 (op1, BS_FLOAT_PREC_BITS);
    mpf_init2 (op2, BS_FLOAT_PREC_BITS);
    mpf_set_z (op1, size1->priv->bytes);
    mpf_set_z (op2, size2->priv->bytes);

    mpf_div (op1, op1, op2);

    gmp_asprintf (&ret, "%.*Fg", BS_FLOAT_PREC_BITS/3, op1);

    mpf_clears (op1, op2, NULL);

    return ret;
}

/**
 * bs_size_true_div_int:
 *
 * Returns: (transfer full): a string representing the floating-point number
 *                           that equals to @size / @divisor
 */
gchar* bs_size_true_div_int (BSSize *size, guint64 divisor, GError **error) {
    mpf_t op1;
    gchar *ret = NULL;

    if (divisor == 0) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_ZERO_DIV,
                     "Division by zero");
        return 0;
    }

    mpf_init2 (op1, BS_FLOAT_PREC_BITS);
    mpf_set_z (op1, size->priv->bytes);

    mpf_div_ui (op1, op1, divisor);

    gmp_asprintf (&ret, "%.*Fg", BS_FLOAT_PREC_BITS/3, op1);

    mpf_clear (op1);

    return ret;
}

/**
 * bs_size_mod:
 *
 * Returns: (transfer full): a #BSSize instance that is a remainder of
 *                           @size1 / @size2 using integer division
 */
BSSize* bs_size_mod (BSSize *size1, BSSize *size2, GError **error) {
    BSSize *ret = NULL;
    if (mpz_cmp_ui (size2->priv->bytes, 0) == 0) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_ZERO_DIV,
                     "Division by zero");
        return 0;
    }


    ret = bs_size_new ();
    mpz_mod (ret->priv->bytes, size1->priv->bytes, size2->priv->bytes);

    return ret;
}

/**
 * bs_size_round_to_nearest:
 *
 * Returns: (transfer full): a new instance of #BSSize that is @size rounded to
 *                           a multiple of @round_to according to @dir
 */
BSSize* bs_size_round_to_nearest (BSSize *size, BSSize *round_to, BSRoundDir dir, GError **error) {
    BSSize *ret = NULL;
    mpz_t q;

    if (mpz_cmp_ui (round_to->priv->bytes, 0) == 0) {
        g_set_error (error, BS_SIZE_ERROR, BS_SIZE_ERROR_ZERO_DIV,
                     "Division by zero");
        return NULL;
    }

    mpz_init (q);

    if (dir == BS_ROUND_DIR_UP)
        mpz_cdiv_q (q, size->priv->bytes, round_to->priv->bytes);
    else
        mpz_fdiv_q (q, size->priv->bytes, round_to->priv->bytes);

    ret = bs_size_new ();
    mpz_mul (ret->priv->bytes, q, round_to->priv->bytes);

    mpz_clear (q);

    return ret;
}


/***************
 * COMPARISONS *
 ***************/
/**
 * bs_size_cmp:
 *
 * Returns: -1, 0, or 1 if @size1 is smaller, equal to or bigger than
 *          @size2 respectively comparing absolute values if @abs is %TRUE
 */
gint bs_size_cmp (BSSize *size1, BSSize *size2, gboolean abs) {
    if (abs)
        return mpz_cmpabs (size1->priv->bytes, size2->priv->bytes);
    else
        return mpz_cmp (size1->priv->bytes, size2->priv->bytes);
}

/**
 * bs_size_cmp_bytes:
 *
 * Returns: -1, 0, or 1 if @size1 is smaller, equal to or bigger than
 *          @bytes respectively comparing absolute values if @abs is %TRUE
 */
gint bs_size_cmp_bytes (BSSize *size1, guint64 bytes, gboolean abs) {
    if (abs)
        return mpz_cmpabs_ui (size1->priv->bytes, bytes);
    else
        return mpz_cmp_ui (size1->priv->bytes, bytes);
}
