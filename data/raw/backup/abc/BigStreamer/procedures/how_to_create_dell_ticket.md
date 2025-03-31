# BigStreamer - How to Open a Ticket to DELL

## Description
This procedure describes the step-by-step process of opening a support ticket with DELL and collecting TSR logs from IDRAC.

## Prerequisites
- SSH access to the issue node.
- `ipmitool` package installed (install if missing).
- VNC access to the node.
- Dell support contact information.
- Permission to inform `abc` before performing any action on IDRAC.

## Procedure Steps

### 1. SSH into the Issue Node
- Connect to the node using your personal account:
  ```bash
  ssh user@<issue-node>
  ```

### 2. Identify the Management IP
- Gain root privileges and retrieve the management IP:
  ```bash
  sudo -i
  ipmitool lan print | grep -i 'IP Address'
  ```
- Alternatively, search for the node's IP in the hosts file:
  ```bash
  grep nodew /etc/hosts
  ```
- If `ipmitool` is missing, install it:
  ```bash
  yum install ipmitool
  ```

### 3. Connect to the IDRAC Web Interface
- Open a VNC session to the node.
- Launch Firefox and enter the **Management IP** retrieved in Step 2.

### 4. Retrieve the Service Tag Number
- Navigate to:
  ```
  Server → Overview → Server Information
  ```
- Copy the **Service Tag Number**.

### 5. Contact Dell Support
- Call Dell support at:
  ```
  +30 2108129800
  ```
- Provide the **Service Tag Number** retrieved in Step 4.
- Dell support will create a case and provide further instructions.

### 6. Collect TSR Logs from IDRAC
- If Dell does not provide a direct guide, follow the official documentation:
  ```
  https://www.dell.com/support/kbdoc/el-gr/000126803/export-a-supportassist-collection-via-idrac7-and-idrac8
  ```
- Inform `abc` before performing any action on IDRAC.

### 7. Download TSR Logs Locally
- SSH into the node using VNC (e.g., `un4`).
- The downloaded files are stored under:
  ```
  /home/cloudera/Downloads/
  ```
- File format:
  ```
  TSRdate_service_tag.zip
  ```

### 8. Send the Logs to Dell
- Email the collected TSR log files to Dell support and wait for their response.

## Actions Taken / Expected Output
- A support ticket is successfully created with Dell.
- TSR logs are collected and sent to Dell for analysis.
- Await Dell's response with further troubleshooting steps or solutions.

## Notes and Warnings
> Ensure `abc` is informed before performing any action on IDRAC.  
> Keep a copy of the TSR logs until the issue is resolved.

## Affected Systems / Scope
- BigStreamer platform.
- Servers managed via IDRAC.

## Troubleshooting / Error Handling
- If `ipmitool` is missing, install it with:
  ```bash
  yum install ipmitool
  ```
- If unable to connect via VNC, verify network settings.
- If Dell support does not respond, follow up with the provided case reference number.

## References
- [Export SupportAssist Collection via IDRAC](https://www.dell.com/support/kbdoc/el-gr/000126803/export-a-supportassist-collection-via-idrac7-and-idrac8)

