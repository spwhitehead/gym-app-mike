export interface RegistrationDataInput {
  username: string;
  hashed_password: string;
  first_name: string;
  last_name: string;
  birthday: string;
  body_weight: number;
  height: number;
  gender: "male" | "female";
}
