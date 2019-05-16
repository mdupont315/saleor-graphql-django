import InputAdornment from "@material-ui/core/InputAdornment";
import {
  createStyles,
  Theme,
  withStyles,
  WithStyles
} from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import * as React from "react";

const styles = (theme: Theme) =>
  createStyles({
    currencySymbol: {
      fontSize: "0.875rem"
    },
    inputContainer: {
      display: "grid",
      gridTemplateColumns: "1fr 2rem 1fr"
    },
    pullDown: {
      marginTop: theme.spacing.unit * 2
    },
    separator: {
      marginTop: theme.spacing.unit * 3,
      textAlign: "center",
      width: "100%"
    },
    widgetContainer: {
      marginTop: theme.spacing.unit * 2
    }
  });

interface PriceFieldProps extends WithStyles<typeof styles> {
  currencySymbol?: string;
  disabled?: boolean;
  error?: boolean;
  hint?: string;
  label?: string;
  name?: string;
  value?: string | number;
  onChange(event: any);
}

export const PriceField = withStyles(styles, { name: "PriceField" })(
  ({
    disabled,
    error,
    label,
    hint,
    currencySymbol,
    name,
    classes,
    onChange,
    value
  }: PriceFieldProps) => (
    <TextField
      error={error}
      helperText={hint}
      label={label}
      value={value}
      InputProps={{
        endAdornment: currencySymbol ? (
          <InputAdornment position="end" className={classes.currencySymbol}>
            {currencySymbol}
          </InputAdornment>
        ) : (
          <span />
        ),
        type: "number"
      }}
      name={name}
      disabled={disabled}
      onChange={onChange}
    />
  )
);
PriceField.defaultProps = {
  name: "price"
};

PriceField.displayName = "PriceField";
export default PriceField;
