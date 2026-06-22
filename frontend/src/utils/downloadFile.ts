/**
 * Download a text file with the user's electricity ID
 * Usage Example: downloadElectricityId('ELEC-123456', 'my-electricity-id.txt')
 */


export function downloadElectricityId(electricityId: string, filename = 'electricity-id.txt') : void {
    const content = `Your Electricity Platform ID\n==================\n${electricityId}\n\nKeep this ID safe. You'll need it to log in.`;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Clean up the URL object
    URL.revokeObjectURL(url);
};