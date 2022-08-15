import React from "react";
import { Text, Stack, Image } from "@fluentui/react";
import logo from "../../assets/logo.svg";

const Navbar: React.FunctionComponent = () => {
  return (
    <Stack horizontal verticalAlign="center" style={{ padding: 3, backgroundColor: "lightskyblue" }}>
      <Image src={logo} alt="logo" style={{ height: "3vh" }} />
      <Text variant="xLarge" style={{ margin: 5 }}>Process Twins</Text>
    </Stack>
  );
};

export default Navbar;
