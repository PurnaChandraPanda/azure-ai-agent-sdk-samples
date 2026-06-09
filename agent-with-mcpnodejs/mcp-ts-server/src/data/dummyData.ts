export type DummyPlayer = {
  extProfileId: string;
  firstName: string;
  lastName: string;
  email: string;
  phoneNumber: string;
  patronId: string;
  profileType: "EXTERNAL" | "LOCAL";
};

export const dummyPlayers: DummyPlayer[] = [
  {
    extProfileId: "EXT-1001",
    firstName: "John",
    lastName: "Doe",
    email: "john.doe@example.com",
    phoneNumber: "5551234567",
    patronId: "PATRON-1001",
    profileType: "EXTERNAL"
  },
  {
    extProfileId: "EXT-1002",
    firstName: "Jane",
    lastName: "Smith",
    email: "jane.smith@example.com",
    phoneNumber: "5559876543",
    patronId: "PATRON-1002",
    profileType: "EXTERNAL"
  },
  {
    extProfileId: "EXT-1003",
    firstName: "Purna",
    lastName: "Panda",
    email: "purna.panda@example.com",
    phoneNumber: "5551112222",
    patronId: "PATRON-1003",
    profileType: "EXTERNAL"
  }
];

export const dummyPropertyConfig = {
  propertyId: "PROP-001",
  propertyName: "Demo Golf Club",
  isCgpsEnabled: false,
  localSearchEnabled: true
};

export const dummyTeeTimes = [
  {
    teeTimeId: "TT-9001",
    propertyId: "PROP-001",
    courseName: "East Course",
    startTime: "2026-06-06T08:30:00Z",
    availableSlots: 4,
    pricePerPlayer: 75
  },
  {
    teeTimeId: "TT-9002",
    propertyId: "PROP-001",
    courseName: "West Course",
    startTime: "2026-06-06T09:10:00Z",
    availableSlots: 2,
    pricePerPlayer: 95
  }
];