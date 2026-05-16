export class AdminModel {
  id: string;
  email: string;
  role: string;

  constructor(params: { id: string; email: string; role: string }) {
    this.id = params.id;
    this.email = params.email;
    this.role = params.role;
  }
}
